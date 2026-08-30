#!/usr/bin/env python3
"""Count tool and Bash command usage by agent across Claude Code transcripts.

Usage:
  agent-tool-usage.py analyze [-a agent-type]... [--dir DIR]
  agent-tool-usage.py markdown [--top N | --min N] [FILE]

analyze: with no -a given, reports every agent found. Output JSON has
two roots: "tools" (tool calls by tool name) and "bash" (Bash commands —
built-in Bash and MCP mcp__*__bash tools — grouped by executable;
compound commands count each segment's executable). Each root has
"agents" (per-agent counts) and "total" (merged counts). A third
root, "sessions", counts distinct sessions by year-month.

markdown: convert analyze's JSON output (from FILE or stdin) to Markdown.
--top N keeps only the N highest-count rows per table; --min N keeps
only rows with count >= N (mutually exclusive). Neither filters the
sessions table.

Example: agent-tool-usage.py analyze -a andrewrabert-dev:requirements
"""

import argparse
import json
import os
import re
import shlex
import sys
from collections import Counter, defaultdict
from pathlib import Path

MAIN = "(main)"
UNKNOWN = "(unknown-sidechain)"
UNPARSABLE = "(unparsable)"

LABEL_PARAM = {
    "Agent": "subagent_type",
    "Task": "subagent_type",
    "Skill": "skill",
}
DEFAULT_SUBAGENT = "general-purpose"
EXCLUDED_PARAMS = {
    "Agent": {"prompt", "description"},
    "Task": {"prompt", "description"},
    "Skill": {"args"},
}

# words that wrap another command; the real command follows
WRAPPERS = {
    "sudo",
    "doas",
    "command",
    "nohup",
    "time",
    "env",
    "exec",
    "builtin",
    "nice",
    "stdbuf",
    "timeout",
}
# wrapper flags that take a value (skip the value too)
WRAPPER_VALUE_FLAGS = {"-u", "-n", "-i", "-o", "-e", "-s", "-k"}
ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
SEPARATORS = {"&&", "||", "|", ";", "&", "|&", ";;", "(", ")", "{", "}"}
HEREDOC_RE = re.compile(r"<<-?\s*\\?(['\"]?)(\w+)\1")
# next token is a command
KEYWORDS_PRE_CMD = {"if", "then", "else", "elif", "while", "until", "do", "!"}
# next token is not a command (loop vars, patterns, closers, tests)
KEYWORDS_NON_CMD = {
    "for",
    "case",
    "select",
    "in",
    "function",
    "fi",
    "done",
    "esac",
    "[[",
    "]]",
    "[",
    "]",
}


def lines(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def blocks(e):
    msg = e.get("message")
    if isinstance(msg, dict) and isinstance(msg.get("content"), list):
        for b in msg["content"]:
            if isinstance(b, dict):
                yield b


def tool_label(b, json_params=False):
    name = b["name"]
    if name not in LABEL_PARAM:
        return name
    inp = b.get("input")
    if not isinstance(inp, dict):
        return name
    if json_params:
        kept = {k: v for k, v in inp.items() if k not in EXCLUDED_PARAMS[name]}
        params = json.dumps(kept, sort_keys=True, separators=(",", ":"))
        return f"{name}({params})"
    param = inp.get(LABEL_PARAM[name])
    if not param and name in ("Agent", "Task"):
        param = DEFAULT_SUBAGENT
    return f"{name}({param})" if param else name


def is_bash_tool(name):
    return name == "Bash" or (
        isinstance(name, str) and name.lower().endswith("__bash")
    )


def strip_heredocs(command):
    """Drop heredoc bodies (and their terminator lines) from a command."""
    kept = []
    pending = []
    for line in command.split("\n"):
        if pending:
            if line.strip() == pending[0]:
                pending.pop(0)
            continue
        pending.extend(m.group(2) for m in HEREDOC_RE.finditer(line))
        kept.append(line)
    return "\n".join(kept)


def tokenize(command):
    lex = shlex.shlex(command, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    return list(lex)


def executables(command):
    """Yield the executable name of each simple command in a shell string."""
    try:
        tokens = tokenize(strip_heredocs(command))
    except ValueError:
        yield UNPARSABLE
        return
    expect_cmd = True
    skip_values = False
    for tok in tokens:
        if tok in SEPARATORS or tok.endswith(("&&", "||", ";", "|")):
            expect_cmd = True
            skip_values = False
            continue
        if not expect_cmd:
            continue
        if tok in KEYWORDS_PRE_CMD:
            continue
        if tok in KEYWORDS_NON_CMD:
            expect_cmd = False
            continue
        if ASSIGN_RE.match(tok):
            continue
        if skip_values and (
            tok in WRAPPER_VALUE_FLAGS or tok.startswith("-") or tok.isdigit()
        ):
            continue
        name = os.path.basename(tok)
        if name in WRAPPERS:
            skip_values = name in ("env", "timeout", "nice", "stdbuf")
            continue
        yield name
        expect_cmd = False
        skip_values = False


def entry_labels(e, json_params):
    """(tool labels, bash executables) for one assistant entry."""
    tools = []
    bash = []
    for b in blocks(e):
        if b.get("type") != "tool_use" or not b.get("name"):
            continue
        tools.append(tool_label(b, json_params))
        if not is_bash_tool(b["name"]) or not isinstance(b.get("input"), dict):
            continue
        command = b["input"].get("command")
        if isinstance(command, str) and command.strip():
            bash.extend(executables(command))
    return tools, bash


def cmd_analyze(args):
    root = Path(args.dir).expanduser()
    files = sorted(root.rglob("*.jsonl"))
    if not files:
        sys.exit(f"no .jsonl transcripts found under {root}")

    # per-kind counts keyed by final label or provisional ("agentid", id)
    counts = {"tools": defaultdict(Counter), "bash": defaultdict(Counter)}
    tooluse_to_type = {}  # tool_use id -> subagent_type (from Agent/Task calls)
    agentid_to_type = {}  # agentId -> subagent_type (via toolUseResult linkage)
    session_start = {}  # sessionId (or file path) -> earliest timestamp

    for f in files:
        for e in lines(f):
            ts = e.get("timestamp")
            if isinstance(ts, str) and ts:
                sid = e.get("sessionId") or str(f)
                if sid not in session_start or ts < session_start[sid]:
                    session_start[sid] = ts
            tur = e.get("toolUseResult")
            spawned_id = tur.get("agentId") if isinstance(tur, dict) else None
            for b in blocks(e):
                bt = b.get("type")
                if (
                    bt == "tool_use"
                    and b.get("name") in ("Task", "Agent")
                    and isinstance(b.get("input"), dict)
                ):
                    st = b["input"].get("subagent_type") or DEFAULT_SUBAGENT
                    if b.get("id"):
                        tooluse_to_type[b["id"]] = st
                elif (
                    bt == "tool_result"
                    and spawned_id
                    and b.get("tool_use_id") in tooluse_to_type
                ):
                    agentid_to_type[spawned_id] = tooluse_to_type[
                        b["tool_use_id"]
                    ]

            if e.get("type") != "assistant":
                continue
            tools, bash = entry_labels(e, args.json_params)
            if not tools and not bash:
                continue
            attr = (
                e.get("attributionAgent")
                or e.get("subagentType")
                or e.get("agentType")
            )
            if attr:
                key = attr
            elif e.get("agentId"):
                key = ("agentid", e["agentId"])
            elif e.get("isSidechain"):
                key = UNKNOWN
            else:
                key = MAIN
            for label in tools:
                counts["tools"][key][label] += 1
            for label in bash:
                counts["bash"][key][label] += 1

    # resolve provisional agentId keys
    for kind, kc in counts.items():
        resolved = defaultdict(Counter)
        for key, c in kc.items():
            if isinstance(key, tuple):
                key = agentid_to_type.get(key[1], UNKNOWN)
            resolved[key] += c
        counts[kind] = resolved

    found_agents = set(counts["tools"]) | set(counts["bash"])
    if args.agent:
        missing = [a for a in args.agent if a not in found_agents]
        if missing:
            found = ", ".join(sorted(found_agents)) or "none"
            sys.exit(
                f"no tool calls found for agent(s) {', '.join(missing)} "
                f"({len(files)} transcripts scanned; agents found: {found})"
            )
        agents = args.agent
    else:
        agents = sorted(
            found_agents,
            key=lambda a: -sum(counts["tools"][a].values()),
        )

    out = {}
    for kind, kc in counts.items():
        total = Counter()
        for agent in agents:
            total += kc[agent]
        out[kind] = {
            "agents": {
                agent: dict(kc[agent].most_common()) for agent in agents
            },
            "total": dict(total.most_common()),
        }
    months = Counter(ts[:7] for ts in session_start.values())
    out["sessions"] = dict(sorted(months.items()))
    json.dump(out, sys.stdout, indent=2)
    print()


def md_table(counter, headers, top=None, minimum=None):
    items = sorted(counter.items(), key=lambda kv: -kv[1])
    if top is not None:
        items = items[:top]
    elif minimum is not None:
        items = [(k, v) for k, v in items if v >= minimum]
    rows = [f"| {headers[0]} | {headers[1]} |", "| --- | ---: |"]
    for name, count in items:
        cell = name.replace("|", "\\|")
        rows.append(f"| {cell} | {count} |")
    rows.append("")
    return rows


def cmd_markdown(args):
    if args.file and args.file != "-":
        with open(args.file, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    out = []
    titles = {"tools": "Tools", "bash": "Bash Commands"}
    columns = {"tools": "Tool", "bash": "Command"}
    for kind in ("tools", "bash"):
        section = data.get(kind)
        if not isinstance(section, dict):
            continue
        out.append(f"# {titles[kind]}")
        out.append("")
        for agent, counter in section.get("agents", {}).items():
            out.append(f"## {agent}")
            out.append("")
            out.extend(
                md_table(
                    counter,
                    (columns[kind], "Count"),
                    top=args.top,
                    minimum=args.min,
                )
            )
        total = section.get("total")
        if total:
            out.append("## Total")
            out.append("")
            out.extend(
                md_table(
                    total,
                    (columns[kind], "Count"),
                    top=args.top,
                    minimum=args.min,
                )
            )
    sessions = data.get("sessions")
    if sessions:
        out.append("# Sessions")
        out.append("")
        out.extend(md_table(sessions, ("Month", "Count")))
    print("\n".join(out).rstrip())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)

    ana = sub.add_parser(
        "analyze",
        help="scan transcripts and emit usage counts as JSON",
    )
    ana.add_argument(
        "-a",
        "--agent",
        action="append",
        default=[],
        help="agent type to report on (repeatable); omit for all agents",
    )
    default_dir = (
        Path(os.environ["CLAUDE_CONFIG_DIR"]) / "projects"
        if os.environ.get("CLAUDE_CONFIG_DIR")
        else Path.home() / ".claude" / "projects"
    )
    ana.add_argument("--dir", default=str(default_dir))
    ana.add_argument(
        "--json-params",
        action="store_true",
        help="label Agent/Task/Skill calls with a JSON dump of their "
        "non-excluded params instead of key=value pairs",
    )
    ana.set_defaults(func=cmd_analyze)

    md = sub.add_parser(
        "markdown",
        help="convert analyze's JSON output to Markdown",
    )
    md.add_argument(
        "file",
        nargs="?",
        help="JSON file from the analyze subcommand (default: stdin)",
    )
    group = md.add_mutually_exclusive_group()
    group.add_argument(
        "--top",
        type=int,
        metavar="N",
        help="show only the top N rows of each table",
    )
    group.add_argument(
        "--min",
        type=int,
        metavar="N",
        help="show only rows with count >= N",
    )
    md.set_defaults(func=cmd_markdown)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
