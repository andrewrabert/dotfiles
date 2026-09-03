#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pydantic"]
# ///
"""Generate an agent-flow Gantt page from a Claude Code session transcript.

Usage:
    scripts/gen-agent-flow.py (--session ID | --session-path JSONL)
                              [-o OUTPUT_HTML] [--subtitle TEXT]

Reads the main transcript plus its subagents/ directory and emits a
self-contained HTML page: per-agent timeline bars, token stats, and every
user prompt marked on the timeline with full text below.
"""

import abc
import argparse
import collections.abc
import contextlib
import datetime
import html
import json
import os
import pathlib
import string
import sys
import tempfile
import typing

import pydantic


class UserError(Exception):
    """An expected input or filesystem error suitable for CLI display."""


class TokenUsage(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="ignore", frozen=True)

    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            **{
                name: getattr(self, name) + getattr(other, name)
                for name in type(self).model_fields
            }
        )


class TranscriptMessage(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="ignore", frozen=True)

    usage: TokenUsage | None = None
    model: str | None = None
    content: typing.Any = None


class TranscriptRecord(pydantic.BaseModel, abc.ABC):
    model_config = pydantic.ConfigDict(extra="ignore", frozen=True)

    uuid: str | None = None
    parentUuid: str | None = None
    timestamp: datetime.datetime | None = None
    effort: str | None = None
    message: TranscriptMessage = pydantic.Field(
        default_factory=TranscriptMessage
    )

    @abc.abstractmethod
    def _concrete(self) -> None:
        pass

    @classmethod
    def from_str(cls, line: str) -> "TranscriptRecord":
        value = json.loads(line)
        record_type = value.get("type") if isinstance(value, dict) else None
        record_class: type[TranscriptRecord]
        if record_type == "user":
            record_class = UserRecord
        elif record_type == "assistant":
            record_class = AssistantRecord
        else:
            record_class = UnknownRecord
        return record_class.model_validate(value)


class UserRecord(TranscriptRecord):
    type: typing.Literal["user"]

    def _concrete(self) -> None:
        pass


class AssistantRecord(TranscriptRecord):
    type: typing.Literal["assistant"]

    def _concrete(self) -> None:
        pass


class UnknownRecord(TranscriptRecord):
    type: typing.Any = None
    message: typing.Any = None

    def _concrete(self) -> None:
        pass


class AgentMetadata(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="ignore", frozen=True)

    toolUseId: str | None = None
    agentType: str = "?"
    description: str | None = None


class DomainModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        extra="forbid", frozen=True, strict=True
    )


class TranscriptStats(DomainModel):
    first_timestamp: float | None
    last_timestamp: float | None
    tokens: TokenUsage
    model: str
    effort: str


class Transcript(DomainModel):
    model_config = pydantic.ConfigDict(
        extra="forbid", frozen=True, strict=True, arbitrary_types_allowed=True
    )

    source: pathlib.Path
    live: tuple[TranscriptRecord, ...]
    abandoned_count: int


class AgentTranscript(DomainModel):
    id: str
    metadata: AgentMetadata
    stats: TranscriptStats
    tool_ids: frozenset[str]
    abandoned_count: int


class AgentNode(DomainModel):
    transcript: AgentTranscript
    parent: str


class AgentRow(DomainModel):
    id: str
    type: str
    desc: str
    parent: str | None
    depth: int
    start: float
    dur: float
    model: str
    effort: str
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int


class Prompt(DomainModel):
    t: float
    text: str


class Extraction(DomainModel):
    agents: tuple[AgentRow, ...]
    prompts: tuple[Prompt, ...]
    abandoned_count: int
    excluded_agent_count: int


class RenderInput(DomainModel):
    short_id: str
    subtitle: str
    agents: tuple[AgentRow, ...]
    prompts: tuple[Prompt, ...]
    type_slot: dict[str, list[str]]
    light_vars: str
    dark_vars: str
    t_max: int
    tick_step: int
    t_end: float


class TranscriptRepository:
    """Filesystem adapter for transcript records and subagent metadata."""

    def load_records(self, path: pathlib.Path) -> list[TranscriptRecord]:
        try:
            lines = path.read_text().splitlines()
        except UnicodeDecodeError as exc:
            raise UserError(f"{path}: invalid UTF-8") from exc
        except OSError as exc:
            raise UserError(f"{path}: {exc.strerror or exc}") from exc

        records: list[TranscriptRecord] = []
        for line_number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                records.append(TranscriptRecord.from_str(line))
            except json.JSONDecodeError:
                # Claude transcripts may contain interrupted/truncated lines.
                continue
            except pydantic.ValidationError as exc:
                raise UserError(
                    f"{path}: record {line_number}: {format_validation_error(exc)}"
                ) from exc
        return records

    def load_metadata(self, path: pathlib.Path) -> AgentMetadata:
        try:
            value = json.loads(path.read_text())
        except UnicodeDecodeError as exc:
            raise UserError(f"{path}: invalid UTF-8") from exc
        except json.JSONDecodeError as exc:
            raise UserError(
                f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}"
            ) from exc
        except OSError as exc:
            raise UserError(f"{path}: {exc.strerror or exc}") from exc
        try:
            return AgentMetadata.model_validate(value)
        except pydantic.ValidationError as exc:
            raise UserError(f"{path}: {format_validation_error(exc)}") from exc

    def load_transcript(self, path: pathlib.Path) -> Transcript:
        return build_transcript(self.load_records(path), path)

    def load_subagents(
        self, main_path: pathlib.Path
    ) -> tuple[AgentTranscript, ...]:
        subdir = main_path.with_suffix("") / "subagents"
        entries = list_directory(subdir, missing_ok=True)

        metadata_paths = sorted(
            subdir / entry.name
            for entry in entries
            if entry.name.startswith("agent-")
            and entry.name.endswith(".meta.json")
        )
        agents: list[AgentTranscript] = []
        for metadata_path in metadata_paths:
            agent_id = metadata_path.name[len("agent-") : -len(".meta.json")]
            transcript = self.load_transcript(
                subdir / f"agent-{agent_id}.jsonl"
            )
            agents.append(
                AgentTranscript(
                    id=agent_id,
                    metadata=self.load_metadata(metadata_path),
                    stats=calculate_stats(transcript.live),
                    tool_ids=find_tool_use_ids(transcript.live),
                    abandoned_count=transcript.abandoned_count,
                )
            )
        return tuple(agents)


def list_directory(
    path: pathlib.Path, *, missing_ok: bool = False
) -> tuple[os.DirEntry[str], ...]:
    try:
        with os.scandir(path) as iterator:
            return tuple(sorted(iterator, key=lambda entry: entry.name))
    except FileNotFoundError as exc:
        if missing_ok:
            return ()
        raise UserError(f"{path}: {exc.strerror or exc}") from exc
    except OSError as exc:
        raise UserError(f"{path}: {exc.strerror or exc}") from exc


def entry_is_directory(entry: os.DirEntry[str]) -> bool:
    try:
        return entry.is_dir()
    except OSError as exc:
        raise UserError(f"{entry.path}: {exc.strerror or exc}") from exc


def find_projects_directories(
    config_root: pathlib.Path,
) -> tuple[pathlib.Path, ...]:
    root_entries = list_directory(config_root)
    projects_directories: list[pathlib.Path] = []
    for entry in root_entries:
        if not entry_is_directory(entry):
            if entry.name == "projects":
                raise UserError(f"{entry.path}: not a directory")
            continue

        directory = pathlib.Path(entry.path)
        if entry.name == "projects":
            projects_directories.append(directory)
            continue

        for profile_entry in list_directory(directory):
            if profile_entry.name != "projects":
                continue
            if not entry_is_directory(profile_entry):
                raise UserError(f"{profile_entry.path}: not a directory")
            projects_directories.append(pathlib.Path(profile_entry.path))

    if not projects_directories:
        raise UserError(f"{config_root}: no projects directories found")
    return tuple(sorted(projects_directories))


def find_session_matches(
    config_root: pathlib.Path, session_prefix: str
) -> tuple[pathlib.Path, ...]:
    matches: list[pathlib.Path] = []
    for projects_directory in find_projects_directories(config_root):
        for project_entry in list_directory(projects_directory):
            if not entry_is_directory(project_entry):
                continue
            project_directory = pathlib.Path(project_entry.path)
            for session_entry in list_directory(project_directory):
                name = session_entry.name
                if (
                    name == "history.jsonl"
                    or not name.endswith(".jsonl")
                    or not name[: -len(".jsonl")].startswith(session_prefix)
                ):
                    continue
                try:
                    is_file = session_entry.is_file()
                except OSError as exc:
                    raise UserError(
                        f"{session_entry.path}: {exc.strerror or exc}"
                    ) from exc
                if is_file:
                    matches.append(pathlib.Path(session_entry.path))
    return tuple(sorted(matches))


def config_root_from_environment() -> pathlib.Path:
    configured = os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude")
    return pathlib.Path(configured).expanduser()


def resolve_session_prefix(session_prefix: str) -> pathlib.Path:
    matches = find_session_matches(
        config_root_from_environment(), session_prefix
    )
    if not matches:
        raise UserError(f"no session matches ID prefix {session_prefix!r}")
    if len(matches) > 1:
        candidates = ", ".join(str(path) for path in matches)
        raise UserError(
            f"session ID prefix {session_prefix!r} is ambiguous; matches: {candidates}"
        )
    return next(iter(matches))


def format_validation_error(error: pydantic.ValidationError) -> str:
    detail = error.errors()[0]
    location = ".".join(str(part) for part in detail["loc"])
    return f"{location}: {detail['msg']}" if location else detail["msg"]


def timestamp_seconds(value: datetime.datetime) -> float:
    return value.timestamp()


def calculate_stats(
    records: collections.abc.Iterable[TranscriptRecord],
) -> TranscriptStats:
    first = last = None
    tokens = TokenUsage()
    models: dict[str, int] = {}
    efforts: dict[str, int] = {}
    for record in records:
        if record.timestamp is not None:
            timestamp = timestamp_seconds(record.timestamp)
            first = timestamp if first is None else min(first, timestamp)
            last = timestamp if last is None else max(last, timestamp)
        if isinstance(record, AssistantRecord):
            usage = record.message.usage or TokenUsage()
            tokens += usage
            if record.message.model:
                models[record.message.model] = (
                    models.get(record.message.model, 0) + usage.output_tokens
                )
            if record.effort:
                efforts[record.effort] = (
                    efforts.get(record.effort, 0) + usage.output_tokens
                )
    model = (
        max(models, key=lambda model_name: models[model_name])
        if models
        else "?"
    )
    effort = (
        "+".join(sorted(efforts, key=lambda name: -efforts[name]))
        if efforts
        else "?"
    )
    return TranscriptStats(
        first_timestamp=first,
        last_timestamp=last,
        tokens=tokens,
        model=model,
        effort=effort,
    )


def find_tool_use_ids(
    records: collections.abc.Iterable[TranscriptRecord],
) -> frozenset[str]:
    ids: set[str] = set()
    for record in records:
        if not isinstance(record, AssistantRecord):
            continue
        content = record.message.content
        if not isinstance(content, list):
            continue
        for block in content:
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and isinstance(block.get("id"), str)
            ):
                ids.add(block["id"])
    return frozenset(ids)


def is_user_text(record: TranscriptRecord) -> bool:
    return isinstance(record, UserRecord) and isinstance(
        record.message.content, str
    )


def build_children(
    records: collections.abc.Sequence[TranscriptRecord],
    source: pathlib.Path,
) -> dict[str | None, tuple[str, ...]]:
    known: set[str] = set()
    for record in records:
        if record.uuid in known:
            raise UserError(f"{source}: uuid {record.uuid}: duplicate uuid")
        known.add(typing.cast(str, record.uuid))

    ordered: dict[str | None, list[str]] = {}
    root: str | None = None
    for record in records:
        uuid = typing.cast(str, record.uuid)
        parent = record.parentUuid
        if parent is None:
            if root is not None:
                raise UserError(f"{source}: uuid {uuid}: second root record")
            root = uuid
        elif parent not in known:
            raise UserError(
                f"{source}: uuid {uuid}: parent {parent} is not in the file"
            )
        ordered.setdefault(parent, []).append(uuid)

    children = {parent: tuple(values) for parent, values in ordered.items()}
    reachable: set[str] = set()
    pending = list(children.get(None, ()))
    while pending:
        uuid = pending.pop()
        if uuid in reachable:
            continue
        reachable.add(uuid)
        pending.extend(children.get(uuid, ()))
    for record in records:
        if record.uuid not in reachable:
            raise UserError(
                f"{source}: uuid {record.uuid}: "
                "record is unreachable from the root record"
            )
    return children


def find_abandoned_uuids(
    records_by_uuid: collections.abc.Mapping[str, TranscriptRecord],
    children: collections.abc.Mapping[str | None, tuple[str, ...]],
) -> frozenset[str]:
    abandoned: set[str] = set()
    for siblings in children.values():
        user_text = [
            uuid for uuid in siblings if is_user_text(records_by_uuid[uuid])
        ]
        if len(user_text) < 2:
            continue
        pending = list(user_text[:-1])
        while pending:
            uuid = pending.pop()
            if uuid in abandoned:
                continue
            abandoned.add(uuid)
            pending.extend(children.get(uuid, ()))
    return frozenset(abandoned)


def build_transcript(
    records: collections.abc.Sequence[TranscriptRecord],
    source: pathlib.Path,
) -> Transcript:
    tree_records = tuple(
        record for record in records if record.uuid is not None
    )
    children = build_children(tree_records, source)
    records_by_uuid = {
        typing.cast(str, record.uuid): record for record in tree_records
    }
    abandoned = find_abandoned_uuids(records_by_uuid, children)
    return Transcript(
        source=source,
        live=tuple(
            record for record in tree_records if record.uuid not in abandoned
        ),
        abandoned_count=len(abandoned),
    )


def spawned_agents(
    agents: collections.abc.Sequence[AgentTranscript],
    main_tool_ids: frozenset[str],
) -> tuple[AgentNode, ...]:
    owner_by_tool_id: dict[str, str] = {
        tool_id: "main" for tool_id in main_tool_ids
    }
    remaining = list(agents)
    nodes: list[AgentNode] = []
    while True:
        matched = [
            agent
            for agent in remaining
            if agent.metadata.toolUseId in owner_by_tool_id
        ]
        if not matched:
            return tuple(nodes)
        for agent in matched:
            tool_id = typing.cast(str, agent.metadata.toolUseId)
            nodes.append(
                AgentNode(transcript=agent, parent=owner_by_tool_id[tool_id])
            )
            remaining.remove(agent)
        for agent in matched:
            for tool_id in agent.tool_ids:
                owner_by_tool_id.setdefault(tool_id, agent.id)


def make_agent_row(
    agent: AgentTranscript,
    parent: str,
    depth: int,
    main_start: float,
) -> AgentRow:
    start_timestamp = agent.stats.first_timestamp or main_start
    end_timestamp = (
        agent.stats.last_timestamp or agent.stats.first_timestamp or main_start
    )
    metadata = agent.metadata
    return AgentRow(
        id=agent.id,
        type=metadata.agentType,
        desc=metadata.description or agent.id,
        parent=parent,
        depth=depth,
        start=round(start_timestamp - main_start, 1),
        dur=round(end_timestamp - start_timestamp, 1),
        model=agent.stats.model,
        effort=agent.stats.effort,
        **agent.stats.tokens.model_dump(),
    )


def build_hierarchy(
    main_stats: TranscriptStats, nodes: collections.abc.Sequence[AgentNode]
) -> tuple[AgentRow, ...]:
    if main_stats.first_timestamp is None or main_stats.last_timestamp is None:
        raise UserError("main transcript has no valid timestamps")
    main_start = main_stats.first_timestamp
    rows = [
        AgentRow(
            id="main",
            type="main",
            desc="Session main loop",
            parent=None,
            depth=0,
            start=0.0,
            dur=round(main_stats.last_timestamp - main_start, 1),
            model=main_stats.model,
            effort=main_stats.effort,
            **main_stats.tokens.model_dump(),
        )
    ]

    def emit(parent_id: str, depth: int) -> None:
        children = sorted(
            (node for node in nodes if node.parent == parent_id),
            key=lambda node: node.transcript.stats.first_timestamp or 0,
        )
        for node in children:
            rows.append(
                make_agent_row(node.transcript, parent_id, depth, main_start)
            )
            emit(node.transcript.id, depth + 1)

    emit("main", 1)
    return tuple(rows)


def extract_prompts(
    transcript: Transcript,
    main_start: float,
) -> tuple[Prompt, ...]:
    prompts: list[Prompt] = []
    for record in transcript.live:
        if not is_user_text(record):
            continue
        content = typing.cast(str, record.message.content)
        stripped_content = content.lstrip()
        if stripped_content.startswith(("<task-notification>", "<command-")):
            continue
        if record.timestamp is None:
            raise UserError(
                f"{transcript.source}: uuid {record.uuid}: "
                "user prompt has no timestamp"
            )
        prompts.append(
            Prompt(
                t=round(timestamp_seconds(record.timestamp) - main_start, 1),
                text=content,
            )
        )
    return tuple(prompts)


def extract(
    main_path: pathlib.Path, repository: TranscriptRepository
) -> Extraction:
    main_transcript = repository.load_transcript(main_path)
    main_stats = calculate_stats(main_transcript.live)
    if main_stats.first_timestamp is None:
        raise UserError(
            f"{main_path}: main transcript has no valid timestamps"
        )
    agents = repository.load_subagents(main_path)
    nodes = spawned_agents(agents, find_tool_use_ids(main_transcript.live))
    return Extraction(
        agents=build_hierarchy(main_stats, nodes),
        prompts=extract_prompts(main_transcript, main_stats.first_timestamp),
        abandoned_count=main_transcript.abandoned_count
        + sum(node.transcript.abandoned_count for node in nodes),
        excluded_agent_count=len(agents) - len(nodes),
    )


PALETTE = [
    ("#4a3aa7", "#9085e9"),
    ("#2a78d6", "#3987e5"),
    ("#eb6834", "#d95926"),
    ("#1baf7a", "#199e70"),
    ("#eda100", "#c98500"),
    ("#e87ba4", "#d55181"),
    ("#008300", "#3fae3f"),
    ("#8b6d3f", "#b3925e"),
    ("#0e8f8f", "#2ab5b5"),
    ("#b03a3a", "#d66060"),
]

TEMPLATE = string.Template(r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agent flow — session $short_id</title>
<style>
  .viz-root {
    color-scheme: light;
    --surface-1: #fcfcfb;
    --page: #f9f9f7;
    --text-primary: #0b0b0b;
    --text-secondary: #52514e;
    --text-muted: #898781;
    --grid: #e1e0d9;
    --baseline: #c3c2b7;
    --border: rgba(11,11,11,0.10);
    --prompt: #c026d3;
$light_vars
  }
  @media (prefers-color-scheme: dark) {
    :root:where(:not([data-theme="light"])) .viz-root {
      color-scheme: dark;
      --surface-1: #1a1a19;
      --page: #0d0d0d;
      --text-primary: #ffffff;
      --text-secondary: #c3c2b7;
      --text-muted: #898781;
      --grid: #2c2c2a;
      --baseline: #383835;
      --border: rgba(255,255,255,0.10);
      --prompt: #e879f9;
$dark_vars
    }
  }
  :root[data-theme="dark"] .viz-root {
    color-scheme: dark;
    --surface-1: #1a1a19;
    --page: #0d0d0d;
    --text-primary: #ffffff;
    --text-secondary: #c3c2b7;
    --text-muted: #898781;
    --grid: #2c2c2a;
    --baseline: #383835;
    --border: rgba(255,255,255,0.10);
    --prompt: #e879f9;
$dark_vars
  }
  * { box-sizing: border-box; }
  body.viz-root {
    margin: 0;
    background: var(--page);
    color: var(--text-primary);
    font: 14px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  .wrap { max-width: 1160px; margin: 0 auto; padding: 28px 24px 64px; }
  header.top { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; }
  h1 { font-size: 20px; font-weight: 650; margin: 0; }
  .sub { color: var(--text-secondary); margin: 4px 0 0; font-size: 13px; }
  .theme-btn {
    font: inherit; font-size: 13px; color: var(--text-secondary);
    background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 6px; padding: 5px 10px; cursor: pointer;
  }
  .kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 20px 0 24px; }
  .tile {
    background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 8px; padding: 12px 14px;
  }
  .tile .label { font-size: 12px; color: var(--text-secondary); }
  .tile .value { font-size: 24px; font-weight: 600; margin-top: 2px; }
  .tile .note { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

  .card {
    background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 8px; padding: 18px 18px 14px;
  }
  .legend { display: flex; flex-wrap: wrap; gap: 6px 18px; margin: 0 0 14px; font-size: 12px; color: var(--text-secondary); }
  .legend .key { display: inline-flex; align-items: center; gap: 6px; }
  .legend .swatch { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
  .legend .swatch.prompt { border-radius: 50%; background: var(--prompt); }

  .gantt-scroll { position: relative; }
  .gantt { display: grid; grid-template-columns: 300px 1fr 128px; column-gap: 0; }
  .gantt .axis-label, .gantt .axis-right {
    font-size: 11px; color: var(--text-muted); padding-bottom: 6px;
    border-bottom: 1px solid var(--baseline);
  }
  .gantt .axis-track { position: relative; border-bottom: 1px solid var(--baseline); }
  .gantt .axis-track span {
    position: absolute; bottom: 6px; transform: translateX(-50%);
    font-size: 11px; color: var(--text-muted);
    font-variant-numeric: tabular-nums;
  }
  .gantt .axis-track span:first-child { transform: none; }
  .gantt .axis-right { text-align: right; }

  .row-label {
    display: flex; align-items: center; gap: 7px;
    padding: 0 12px 0 0; min-height: 30px;
    font-size: 12.5px; color: var(--text-primary);
    white-space: nowrap; overflow: hidden;
  }
  .row-label .tree { color: var(--text-muted); flex: none; }
  .row-label .dot { width: 8px; height: 8px; border-radius: 50%; flex: none; }
  .row-label .name { overflow: hidden; text-overflow: ellipsis; }
  .row-label.depth0 .name { font-weight: 600; }
  .row-track {
    position: relative; min-height: 30px;
    background-image: linear-gradient(to right, var(--grid) 1px, transparent 1px);
    background-size: 12.5% 100%;
    background-repeat: repeat-x;
  }
  .bar {
    position: absolute; top: 50%; transform: translateY(-50%);
    height: 14px; border-radius: 4px; min-width: 3px;
    outline: none;
  }
  .bar:hover, .bar:focus-visible { filter: brightness(1.12); box-shadow: 0 0 0 2px var(--surface-1), 0 0 0 3.5px var(--text-muted); }
  .row-meta {
    display: flex; align-items: center; justify-content: flex-end; gap: 10px;
    min-height: 30px; padding-left: 12px;
    font-size: 12px; color: var(--text-secondary);
    font-variant-numeric: tabular-nums; white-space: nowrap;
  }
  .row-meta .dur { color: var(--text-muted); width: 46px; text-align: right; }
  .row-meta .tok { width: 52px; text-align: right; color: var(--text-primary); }

  .prompt-line {
    position: absolute; width: 0;
    border-left: 1.5px dashed var(--prompt);
    opacity: 0.55; pointer-events: none; z-index: 1;
  }
  .prompt-flag {
    position: absolute; transform: translateX(-50%);
    z-index: 2; cursor: pointer;
    background: var(--prompt); color: #fff;
    font-size: 10px; font-weight: 700; line-height: 1;
    padding: 3px 5px; border-radius: 4px; border: none;
    font-variant-numeric: tabular-nums;
  }
  .prompt-flag:hover, .prompt-flag:focus-visible { filter: brightness(1.15); }

  .foot { margin-top: 10px; font-size: 11.5px; color: var(--text-muted); }

  .tooltip {
    position: fixed; z-index: 10; pointer-events: none;
    background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 12px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.18);
    font-size: 12px; max-width: 320px; display: none;
  }
  .tooltip .t-title { font-weight: 600; font-size: 12.5px; margin-bottom: 2px; display: flex; align-items: center; gap: 6px; }
  .tooltip .t-title .keyline { width: 12px; height: 3px; border-radius: 2px; flex: none; }
  .tooltip .t-sub { color: var(--text-muted); margin-bottom: 6px; }
  .tooltip table { border-collapse: collapse; }
  .tooltip td { padding: 1px 0; }
  .tooltip td:first-child { color: var(--text-secondary); padding-right: 14px; }
  .tooltip td:last-child { text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; }

  .prompts { margin-top: 26px; }
  .prompts h2 { font-size: 15px; font-weight: 650; margin: 0 0 12px; }
  .prompt-card {
    background: var(--surface-1); border: 1px solid var(--border);
    border-left: 3px solid var(--prompt);
    border-radius: 8px; padding: 12px 16px; margin-bottom: 12px;
    scroll-margin-top: 16px;
  }
  .prompt-card.flash { box-shadow: 0 0 0 2px var(--prompt); }
  .prompt-head {
    display: flex; align-items: baseline; gap: 10px; margin-bottom: 6px;
    font-size: 12px; color: var(--text-muted); font-variant-numeric: tabular-nums;
  }
  .prompt-head .pnum { font-weight: 700; color: var(--prompt); }
  .prompt-text {
    margin: 0; white-space: pre-wrap; overflow-wrap: break-word;
    font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, monospace;
    color: var(--text-primary);
  }

  details.tbl { margin-top: 22px; }
  details.tbl summary { cursor: pointer; font-size: 13px; color: var(--text-secondary); }
  .data-table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 12px; }
  .data-table th, .data-table td { padding: 5px 10px; text-align: right; border-bottom: 1px solid var(--grid); font-variant-numeric: tabular-nums; }
  .data-table th { color: var(--text-muted); font-weight: 500; }
  .data-table th:nth-child(-n+2), .data-table td:nth-child(-n+2) { text-align: left; font-variant-numeric: normal; }
  @media (max-width: 780px) {
    .kpis { grid-template-columns: repeat(2, 1fr); }
    .gantt { grid-template-columns: 170px 1fr 110px; }
  }
</style>
</head>
<body class="viz-root">
<div class="wrap">
  <header class="top">
    <div>
      <h1>Agent flow — session <code>$short_id</code></h1>
      <p class="sub">$subtitle · times are elapsed from session start</p>
    </div>
    <button class="theme-btn" id="themeBtn" type="button">Toggle theme</button>
  </header>

  <div class="kpis" id="kpis"></div>

  <div class="card">
    <div class="legend" id="legend"></div>
    <div class="gantt-scroll" id="ganttScroll">
      <div class="gantt" id="gantt"></div>
    </div>
    <p class="foot">Bar position and length = agent runtime (elapsed since session start). Dashed lines = user prompts; click a P badge to jump to its text. Right columns: runtime · output tokens. Hover or focus a bar for the full token breakdown.</p>
  </div>

  <section class="prompts" id="prompts">
    <h2>User prompts</h2>
  </section>

  <details class="tbl">
    <summary>Table view — all agents with full token breakdown</summary>
    <table class="data-table" id="dataTable"></table>
  </details>
</div>

<div class="tooltip" id="tooltip"></div>

<script>
const DATA = $data;
const PROMPTS = $prompts;
const TYPE_SLOT = $type_slot;
const T_MAX = $t_max;
const TICK_STEP_MIN = $tick_step;

function fmtDur(s) {
  s = Math.round(s);
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
  if (h) return h + "h " + m + "m";
  if (m) return m + "m " + (sec ? sec + "s" : "");
  return sec + "s";
}
function fmtTok(n) {
  if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
  if (n >= 1e3) return (n / 1e3).toFixed(1) + "K";
  return String(n);
}
function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}

// KPI tiles
const totals = DATA.reduce((a, r) => {
  a.out += r.output_tokens; a.inp += r.input_tokens;
  a.cw += r.cache_creation_input_tokens; a.cr += r.cache_read_input_tokens;
  return a;
}, { out: 0, inp: 0, cw: 0, cr: 0 });
const kpis = [
  ["Agents", String(DATA.length - 1), "subagents + 1 main loop"],
  ["Prompts", String(PROMPTS.length), "user messages"],
  ["Session runtime", fmtDur(DATA[0].dur), "first to last event"],
  ["Output tokens", fmtTok(totals.out), fmtTok(totals.cr) + " cache reads"],
];
for (const [label, value, note] of kpis) {
  const t = el("div", "tile");
  t.append(el("div", "label", label), el("div", "value", value), el("div", "note", note));
  document.getElementById("kpis").append(t);
}

// Legend
const legendBox = document.getElementById("legend");
for (const type of Object.keys(TYPE_SLOT)) {
  const [name, varName] = TYPE_SLOT[type];
  const k = el("span", "key");
  const sw = el("span", "swatch");
  sw.style.background = "var(" + varName + ")";
  k.append(sw, document.createTextNode(name));
  legendBox.append(k);
}
{
  const k = el("span", "key");
  k.append(el("span", "swatch prompt"), document.createTextNode("user prompt"));
  legendBox.append(k);
}

// Gantt
const gantt = document.getElementById("gantt");
gantt.append(el("div", "axis-label", "agent"));
const axisTrack = el("div", "axis-track");
const maxMin = T_MAX / 60;
for (let m = 0; m <= maxMin; m += TICK_STEP_MIN) {
  const s = el("span", null, m + "m");
  s.style.left = (m / maxMin * 100) + "%";
  axisTrack.append(s);
}
gantt.append(axisTrack);
gantt.append(el("div", "axis-right", "runtime · out tok"));

const tooltip = document.getElementById("tooltip");
function placeTip(x, y) {
  tooltip.style.display = "block";
  const rect = tooltip.getBoundingClientRect();
  let left = x + 14, top = y + 14;
  if (left + rect.width > innerWidth - 8) left = x - rect.width - 14;
  if (top + rect.height > innerHeight - 8) top = y - rect.height - 14;
  tooltip.style.left = Math.max(8, left) + "px";
  tooltip.style.top = Math.max(8, top) + "px";
}
function showTip(r, x, y) {
  tooltip.replaceChildren();
  const title = el("div", "t-title");
  const key = el("span", "keyline");
  key.style.background = "var(" + TYPE_SLOT[r.type][1] + ")";
  title.append(key, document.createTextNode(r.desc));
  const sub = el("div", "t-sub",
    TYPE_SLOT[r.type][0] + " · " + r.model + " · " + r.effort + " effort");
  const tbl = document.createElement("table");
  const rows = [
    ["Started at", "+" + fmtDur(r.start)],
    ["Runtime", fmtDur(r.dur)],
    ["Output tokens", r.output_tokens.toLocaleString()],
    ["Input tokens", r.input_tokens.toLocaleString()],
    ["Cache write", r.cache_creation_input_tokens.toLocaleString()],
    ["Cache read", r.cache_read_input_tokens.toLocaleString()],
  ];
  for (const [k, v] of rows) {
    const tr = document.createElement("tr");
    tr.append(el("td", null, k), el("td", null, v));
    tbl.append(tr);
  }
  tooltip.append(title, sub, tbl);
  placeTip(x, y);
}
function showPromptTip(p, i, x, y) {
  tooltip.replaceChildren();
  const title = el("div", "t-title");
  const key = el("span", "keyline");
  key.style.background = "var(--prompt)";
  title.append(key, document.createTextNode("Prompt " + (i + 1)));
  const sub = el("div", "t-sub", "+" + fmtDur(p.t));
  const txt = el("div", null,
    p.text.length > 220 ? p.text.slice(0, 220) + "…" : p.text);
  tooltip.append(title, sub, txt);
  placeTip(x, y);
}
function hideTip() { tooltip.style.display = "none"; }

const treeGlyph = d => d <= 1 ? "├" : "│ ".repeat(d - 1) + "└";
for (const r of DATA) {
  const color = "var(" + TYPE_SLOT[r.type][1] + ")";

  const label = el("div", "row-label depth" + r.depth);
  if (r.depth > 0) label.append(el("span", "tree", treeGlyph(r.depth)));
  const dot = el("span", "dot");
  dot.style.background = color;
  label.append(dot, el("span", "name", r.desc));
  label.title = r.desc + " (" + TYPE_SLOT[r.type][0] + ")";

  const track = el("div", "row-track");
  const bar = el("div", "bar");
  bar.style.left = (r.start / T_MAX * 100) + "%";
  bar.style.width = Math.max(r.dur / T_MAX * 100, 0.3) + "%";
  bar.style.background = color;
  bar.tabIndex = 0;
  bar.setAttribute("role", "img");
  bar.setAttribute("aria-label",
    r.desc + ", " + TYPE_SLOT[r.type][0] + ", runtime " + fmtDur(r.dur) +
    ", " + r.output_tokens.toLocaleString() + " output tokens");
  bar.addEventListener("pointermove", e => showTip(r, e.clientX, e.clientY));
  bar.addEventListener("pointerleave", hideTip);
  bar.addEventListener("focus", () => {
    const b = bar.getBoundingClientRect();
    showTip(r, b.left + b.width / 2, b.bottom);
  });
  bar.addEventListener("blur", hideTip);
  track.append(bar);

  const meta = el("div", "row-meta");
  meta.append(el("span", "dur", fmtDur(r.dur)), el("span", "tok", fmtTok(r.output_tokens)));

  gantt.append(label, track, meta);
}

// Prompt markers: vertical lines spanning the track column, flag on top
const scrollBox = document.getElementById("ganttScroll");
function layoutPromptMarkers() {
  for (const n of scrollBox.querySelectorAll(".prompt-line, .prompt-flag")) n.remove();
  const tracks = gantt.querySelectorAll(".row-track");
  if (!tracks.length) return;
  const boxR = scrollBox.getBoundingClientRect();
  const firstR = tracks[0].getBoundingClientRect();
  const lastR = tracks[tracks.length - 1].getBoundingClientRect();
  PROMPTS.forEach((p, i) => {
    const x = firstR.left - boxR.left + p.t / T_MAX * firstR.width;
    const line = el("div", "prompt-line");
    line.style.left = x + "px";
    line.style.top = (firstR.top - boxR.top) + "px";
    line.style.height = (lastR.bottom - firstR.top) + "px";
    const flag = el("button", "prompt-flag", "P" + (i + 1));
    flag.type = "button";
    flag.style.left = x + "px";
    flag.style.top = (firstR.top - boxR.top - 20) + "px";
    flag.setAttribute("aria-label", "Prompt " + (i + 1) + " at +" + fmtDur(p.t));
    flag.addEventListener("pointermove", e => showPromptTip(p, i, e.clientX, e.clientY));
    flag.addEventListener("pointerleave", hideTip);
    flag.addEventListener("click", () => {
      hideTip();
      const card = document.getElementById("prompt-" + (i + 1));
      card.scrollIntoView({ behavior: "smooth", block: "start" });
      card.classList.add("flash");
      setTimeout(() => card.classList.remove("flash"), 1500);
    });
    scrollBox.append(line, flag);
  });
}
layoutPromptMarkers();
addEventListener("resize", layoutPromptMarkers);

// Prompt list
const promptsBox = document.getElementById("prompts");
PROMPTS.forEach((p, i) => {
  const card = el("article", "prompt-card");
  card.id = "prompt-" + (i + 1);
  const head = el("div", "prompt-head");
  head.append(el("span", "pnum", "P" + (i + 1)),
              el("span", null, "+" + fmtDur(p.t)));
  card.append(head, el("pre", "prompt-text", p.text));
  promptsBox.append(card);
});

// Table view
const table = document.getElementById("dataTable");
const thead = document.createElement("tr");
for (const h of ["Agent", "Type", "Start", "Runtime", "Out", "In", "Cache write", "Cache read", "Model", "Effort"])
  thead.append(el("th", null, h));
table.append(thead);
for (const r of DATA) {
  const tr = document.createElement("tr");
  const cells = [
    (r.depth >= 2 ? " └ " : "") + r.desc,
    TYPE_SLOT[r.type][0],
    "+" + fmtDur(r.start),
    fmtDur(r.dur),
    r.output_tokens.toLocaleString(),
    r.input_tokens.toLocaleString(),
    r.cache_creation_input_tokens.toLocaleString(),
    r.cache_read_input_tokens.toLocaleString(),
    r.model,
    r.effort,
  ];
  for (const c of cells) tr.append(el("td", null, c));
  table.append(tr);
}

// Theme toggle
document.getElementById("themeBtn").addEventListener("click", () => {
  const root = document.documentElement;
  const cur = root.dataset.theme ||
    (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  root.dataset.theme = cur === "dark" ? "light" : "dark";
});
</script>
</body>
</html>
""")


class Renderer:
    """Prepare render data and substitute it into the page template."""

    def __init__(
        self, session_path: pathlib.Path, extraction: Extraction, subtitle: str
    ) -> None:
        self.input = self._build_input(session_path, extraction, subtitle)

    @staticmethod
    def _nice_axis(total_s: float) -> tuple[int, int]:
        total_min = total_s / 60
        for step in (5, 10, 15, 20, 30, 60, 90, 120):
            if total_min / step <= 9:
                break
        ticks = -(-int(total_min) // step) * step
        if ticks < total_min:
            ticks += step
        return ticks * 60, step

    @classmethod
    def _build_input(
        cls, session_path: pathlib.Path, extraction: Extraction, subtitle: str
    ) -> RenderInput:
        types = ["main"] + sorted(
            {row.type for row in extraction.agents if row.type != "main"}
        )
        type_slot: dict[str, list[str]] = {}
        light: list[str] = []
        dark: list[str] = []
        for index, agent_type in enumerate(types):
            light_value, dark_value = PALETTE[index % len(PALETTE)]
            variable = f"--c-t{index}"
            name = "main loop" if agent_type == "main" else agent_type
            type_slot[agent_type] = [name, variable]
            light.append(f"    {variable}: {light_value};")
            dark.append(f"      {variable}: {dark_value};")

        t_end = max(row.start + row.dur for row in extraction.agents)
        t_max, tick_step = cls._nice_axis(t_end)
        return RenderInput(
            short_id=session_path.name[:6],
            subtitle=subtitle
            or f"{len(extraction.agents) - 1} subagents, "
            f"{len(extraction.prompts)} user prompts",
            agents=extraction.agents,
            prompts=extraction.prompts,
            type_slot=type_slot,
            light_vars="\n".join(light),
            dark_vars="\n".join(dark),
            t_max=t_max,
            tick_step=tick_step,
            t_end=t_end,
        )

    def render(self) -> str:
        return TEMPLATE.substitute(
            short_id=html.escape(self.input.short_id),
            subtitle=html.escape(self.input.subtitle),
            light_vars=self.input.light_vars,
            dark_vars=self.input.dark_vars,
            data=json.dumps([row.model_dump() for row in self.input.agents]),
            prompts=json.dumps(
                [prompt.model_dump() for prompt in self.input.prompts]
            ),
            type_slot=json.dumps(self.input.type_slot),
            t_max=self.input.t_max,
            tick_step=self.input.tick_step,
        )


def write_output(path: pathlib.Path, page: str) -> None:
    temporary_path: pathlib.Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False, dir=path.parent
        ) as handle:
            temporary_path = pathlib.Path(handle.name)
            handle.write(page)
        temporary_path.replace(path)
    except OSError as exc:
        raise UserError(f"{path}: {exc.strerror or exc}") from exc
    finally:
        if temporary_path is not None:
            with contextlib.suppress(FileNotFoundError):
                temporary_path.unlink()


def parse_args(
    argv: collections.abc.Sequence[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--session", metavar="ID")
    source.add_argument("--session-path", metavar="JSONL", type=pathlib.Path)
    parser.add_argument("--subtitle", default="")
    parser.add_argument("-o", "--output", metavar="PATH", type=pathlib.Path)
    return parser.parse_args(argv)


def write_stdout(page: str) -> None:
    try:
        sys.stdout.write(page)
    except (OSError, UnicodeError) as exc:
        raise UserError(f"stdout: {exc}") from exc


def format_summary(
    destination: str, extraction: Extraction, runtime: float
) -> str:
    summary = (
        f"{destination}: {len(extraction.agents) - 1} subagents, "
        f"{len(extraction.prompts)} prompts, runtime {round(runtime)}s"
    )
    if extraction.abandoned_count:
        summary += f", {extraction.abandoned_count} abandoned records"
    if extraction.excluded_agent_count:
        summary += f", {extraction.excluded_agent_count} agents excluded"
    return summary


def run(argv: collections.abc.Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    session_path = (
        resolve_session_prefix(args.session)
        if args.session is not None
        else args.session_path
    )
    extraction = extract(session_path, TranscriptRepository())
    renderer = Renderer(session_path, extraction, args.subtitle)
    page = renderer.render()
    destination = "stdout"
    if args.output is None:
        write_stdout(page)
    else:
        write_output(args.output, page)
        destination = str(args.output)
    print(
        format_summary(destination, extraction, renderer.input.t_end),
        file=sys.stderr,
    )
    return 0


def main() -> None:
    try:
        raise SystemExit(run())
    except UserError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
    except KeyboardInterrupt:
        raise SystemExit(130) from None


if __name__ == "__main__":
    main()
