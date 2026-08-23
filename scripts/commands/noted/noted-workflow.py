#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = ["pydantic>=2,<3"]
# ///

"""A workflow adapter around the noted CLI."""

import argparse
import asyncio
import collections.abc
import sys


class NoteSubject(str):
    _MAX_LEN = 128

    def __new__(cls, value):
        if "\n" in value or "\r" in value:
            raise ValueError("must not contain newlines")
        if len(value) > cls._MAX_LEN:
            raise ValueError("must be 128 characters or less")
        if not value:
            raise ValueError("must not be empty")
        return super().__new__(cls, value)


class NoteName:
    SUBJECT = "SUBJECT.md"
    CONTENT = "CONTENT.md"

    def __init__(self, id, subject):
        self.id = id
        self.subject = subject

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id and self.subject == other.subject

    def __hash__(self):
        return hash((self.id, self.subject))

    def __str__(self):
        return str(self.id)

    @property
    def subject_path(self):
        return f"{self.id}/{self.SUBJECT}"

    @property
    def content_path(self):
        return f"{self.id}/{self.CONTENT}"

    @classmethod
    def next(cls, names, subject):
        next_id = max((name.id for name in names), default=0) + 1
        return cls(next_id, subject)

    @classmethod
    def find(cls, names, note_id):
        matches = [name for name in names if name.id == note_id]
        if len(matches) != 1:
            raise ValueError(f"expected exactly one note with ID {note_id}")
        return matches[0]


class SubjectDocument:
    def __init__(self, name, content):
        self.name = name
        self.content = content


class RequirementNote(SubjectDocument):
    pass


class ADRNote(SubjectDocument):
    pass


class ApprovedPlanNote(SubjectDocument):
    pass


class RejectedPlanNote(SubjectDocument):
    def __init__(self, name, content, reason):
        super().__init__(name, content)
        self.reason = reason


class NotedPath:
    _SEP = "/"

    def __init__(self, val):
        self.parts = self._parse(val)

    def __str__(self):
        return self._SEP.join(self.parts)

    @classmethod
    def _parse(cls, *args):
        stack = [*args]
        parts = []
        while stack:
            val = stack.pop()
            if isinstance(val, str):
                parts.extend([p for p in val.split(cls._SEP) if p])
            elif isinstance(val, NotedPath):
                parts.extend(val.parts)
            elif isinstance(val, collections.abc.Iterable):
                stack.extend(list(val))
            else:
                raise ValueError
        return parts

    def join(self, other):
        return NotedPath(self._parse(self, other))


class ProcessError(Exception):
    def __init__(self, process, message=None, stderr=None):
        self.process = process
        self.message = message
        self.stderr = stderr

    def __str__(self):
        proc = self.process

        text = f"exit {proc.returncode}"
        if self.message is not None:
            text = f"{text} - {self.message}"

        try:
            args = proc._transport._extra["subprocess"].args
        except (AttributeError, KeyError):
            pass
        else:
            text = f"{text}: {args}"
        return text


class Noted:
    def __init__(self, scope=""):
        self.scope = NotedPath(scope)

    def scoped_to(self, other):
        return type(self)(self.scope.join(other))

    async def _run(self, *arguments):
        command = ["noted", f"--scope={self.scope}", *arguments]
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode:
            raise ProcessError(process, stderr=stderr)
        return stdout.decode()

    async def search_paths(self):
        output = await self._run("search", "--mode", "path")
        return [line for line in output.splitlines() if line]

    async def read(self, path=""):
        return await self._run("read", path)

    async def write(self, path, content):
        await self._run("write", path, content)

    async def edit(self, path, old_string, new_string, replace_all):
        command = ["edit", path, old_string, new_string]
        if replace_all:
            command.append("--replace-all")
        await self._run(*command)


class ProjectRequirements:
    def __init__(self, noted):
        self.noted = noted

    async def _names(self):
        return NoteName.parse_filenames(await self.noted.search_paths())

    async def create(self, subject, content):
        name = NoteName.next(await self._names(), subject)
        document = RequirementNote(name=name, content=content)
        await self.noted.write(name.filename, document.content)
        return name

    async def _name(self, note_id):
        return NoteName.find(await self._names(), note_id)

    async def read(self, note_id):
        return await self.noted.read((await self._name(note_id)).filename)

    async def write(self, note_id, content):
        await self.noted.write((await self._name(note_id)).filename, content)

    async def edit(self, note_id, old_string, new_string, replace_all):
        await self.noted.edit(
            (await self._name(note_id)).filename,
            old_string,
            new_string,
            replace_all,
        )


class ProjectArchitectureDecisionRecords:
    def __init__(self, noted):
        self.noted = noted

    async def _names(self):
        return NoteName.parse_filenames(await self.noted.search_paths())

    async def create(self, subject, content):
        name = NoteName.next(await self._names(), subject)
        document = ADRNote(name=name, content=content)
        await self.noted.write(name.filename, document.content)
        return f"{name}\n"

    async def _name(self, note_id):
        return NoteName.find(await self._names(), note_id)

    async def read(self, note_id):
        return await self.noted.read((await self._name(note_id)).filename)

    async def write(self, note_id, content):
        await self.noted.write((await self._name(note_id)).filename, content)

    async def edit(self, note_id, old_string, new_string, replace_all):
        await self.noted.edit(
            (await self._name(note_id)).filename,
            old_string,
            new_string,
            replace_all,
        )


class ProjectContext:
    _PATH = "CONTEXT.md"

    def __init__(self, noted):
        self.noted = noted

    async def read(self):
        return await self.noted.read(self._PATH)

    async def write(self, content):
        await self.noted.write(self._PATH, content)

    async def edit(self, old_string, new_string, replace_all):
        await self.noted.edit(
            self._PATH,
            old_string,
            new_string,
            replace_all,
        )


class ProjectStandards:
    def __init__(self, noted):
        self.noted = noted

    async def read(self):
        paths = sorted(await self.noted.search_paths())
        output = ""
        for path in paths:
            if output and not output.endswith("\n"):
                output += "\n"
            output += f"--- {path} ---\n{await self.noted.read(path)}"
        return output


class PlanIdSequence:
    """Allocate IDs shared by approved and rejected plans."""

    def __init__(self, *sources):
        self.sources = sources

    async def next_name(self, subject):
        names = []
        for source in self.sources:
            names.extend(await source())
        return NoteName.next(names, subject)


class ProjectApprovedPlans:
    def __init__(self, noted):
        self.noted = noted

    async def names(self):
        return NoteName.parse_filenames(await self.noted.search_paths())

    async def create(self, subject, plan):
        plan = ApprovedPlanNote(
            name=await self.ids.next_name(subject), content=plan
        )
        await self.noted.write(plan.name.filename, plan.content)
        return f"{plan.name}\n"

    async def list(self):
        names = sorted(await self.names(), key=lambda name: name.id)
        return "".join(f"{name}\n" for name in names)

    async def read(self, note_id):
        name = NoteName.find(await self.names(), note_id)
        return await self.noted.read(name.filename)


class RejectedPlanFile:
    PLAN = f"PLAN{NoteName.SUFFIX}"
    REASON = f"REASON{NoteName.SUFFIX}"

    def __init__(self, name, filename):
        if filename not in (self.PLAN, self.REASON):
            raise ValueError(f"must be {self.PLAN} or {self.REASON}")
        self.name = name
        self.filename = filename

    def __str__(self):
        return f"{self.name}/{self.filename}"

    @classmethod
    def from_path(cls, path):
        directory, separator, filename = path.rpartition("/")
        if not separator:
            raise ValueError("path must be NAME/FILENAME")
        return cls(NoteName.from_str(directory), filename)


class ProjectRejectedPlans:
    def __init__(self, noted):
        self.noted = noted

    async def _files(self):
        files = {}
        for path in await self.noted.search_paths():
            try:
                file = RejectedPlanFile.from_path(path)
            except ValueError:
                continue
            files.setdefault(file.name, set()).add(file.filename)
        return files

    async def names(self):
        return list(await self._files())

    async def create(self, subject, plan, reason):
        plan = RejectedPlanNote(
            name=await self.ids.next_name(subject),
            content=plan,
            reason=reason,
        )
        name = plan.name
        await self.noted.write(
            str(RejectedPlanFile(name, RejectedPlanFile.PLAN)), plan.content
        )
        await self.noted.write(
            str(RejectedPlanFile(name, RejectedPlanFile.REASON)), plan.reason
        )
        return f"{name}\n"

    async def list(self):
        complete = {RejectedPlanFile.PLAN, RejectedPlanFile.REASON}
        names = sorted(
            (
                name
                for name, filenames in (await self._files()).items()
                if filenames == complete
            ),
            key=lambda name: name.id,
        )
        return "".join(f"{name}\n" for name in names)

    async def read(self, note_id):
        name = NoteName.find(await self.names(), note_id)
        return await self.noted.read(
            str(RejectedPlanFile(name, RejectedPlanFile.PLAN))
        )

    async def reason(self, note_id):
        return await self.noted.read(f"{note_id}/{RejectedPlanFile.REASON}")


class Project:
    def __init__(self):
        noted = Noted()
        self.requirements = ProjectRequirements(
            noted.scoped_to("requirements")
        )
        self.adr = ProjectArchitectureDecisionRecords(noted.scoped_to("adr"))
        self.context = ProjectContext(noted)
        self.standards = ProjectStandards(noted.scoped_to("standards"))
        self.approved_plans = ProjectApprovedPlans(
            noted.scoped_to("plans/approved")
        )
        self.rejected_plans = ProjectRejectedPlans(
            noted.scoped_to("plans/rejected")
        )
        plan_ids = PlanIdSequence(
            self.approved_plans.names, self.rejected_plans.names
        )
        self.approved_plans.ids = plan_ids
        self.rejected_plans.ids = plan_ids


def add_edit_parser(subcommands):
    parser = subcommands.add_parser("edit", help="Replace text")
    parser.add_argument(
        "--id", dest="note_id", type=int, required=True, help="Document ID"
    )
    parser.add_argument("old_string", help="Text to replace")
    parser.add_argument("new_string", help="Replacement text")
    parser.add_argument(
        "--replace-all",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Replace every occurrence",
    )
    parser.set_defaults(operation="edit")


def add_document_commands(parser, content_help):
    subcommands = parser.add_subparsers(dest="operation", required=True)

    create = subcommands.add_parser("create", help=f"Create {content_help}")
    create.add_argument(
        "--subject",
        type=NoteSubject,
        required=True,
        help="Subject for the new document",
    )
    create.add_argument("content", help=f"{content_help} content")

    read = subcommands.add_parser("read", help=f"Read {content_help}")
    read.add_argument(
        "--id", dest="note_id", type=int, required=True, help="Document ID"
    )

    write = subcommands.add_parser("write", help=f"Replace {content_help}")
    write.add_argument(
        "--id", dest="note_id", type=int, required=True, help="Document ID"
    )
    write.add_argument("content", help="Replacement content")

    add_edit_parser(subcommands)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="noted-workflow",
        description="Manage noted project workflow documents.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    standards = commands.add_parser(
        "standards", help="Read all project standards"
    )
    standards.set_defaults(operation="read")

    requirements = commands.add_parser(
        "requirements", help="Manage requirements"
    )
    add_document_commands(requirements, "requirement")

    adr = commands.add_parser(
        "adr", help="Manage architecture decision records"
    )
    add_document_commands(adr, "ADR")

    context = commands.add_parser("context", help="Manage the project context")
    context_commands = context.add_subparsers(dest="operation", required=True)
    context_commands.add_parser("read", help="Read context")
    context_write = context_commands.add_parser(
        "write", help="Replace context"
    )
    context_write.add_argument("content", help="Context content")
    context_edit = context_commands.add_parser(
        "edit", help="Replace context text"
    )
    context_edit.add_argument("old_string", help="Text to replace")
    context_edit.add_argument("new_string", help="Replacement text")
    context_edit.add_argument(
        "--replace-all", action=argparse.BooleanOptionalAction, default=False
    )

    for command, help_text, rejected in (
        ("approved-plan", "Manage approved plans", False),
        ("rejected-plan", "Manage rejected plans", True),
    ):
        plan = commands.add_parser(command, help=help_text)
        plan_commands = plan.add_subparsers(dest="operation", required=True)
        create = plan_commands.add_parser("create", help="Create a plan")
        create.add_argument(
            "--subject",
            type=NoteSubject,
            required=True,
            help="Subject for the new plan",
        )
        create.add_argument("plan", help="Plan content")
        if rejected:
            create.add_argument("reason", type=str, help="Rejection reason")
        plan_commands.add_parser("list", help="List plans")
        read = plan_commands.add_parser("read", help="Read a plan")
        read.add_argument(
            "--id", dest="note_id", type=int, required=True, help="Plan ID"
        )
        if rejected:
            reason = plan_commands.add_parser(
                "reason", help="Read rejection reason"
            )
            reason.add_argument(
                "--id", dest="note_id", type=int, required=True, help="Plan ID"
            )

    return parser


async def run(args):
    project = Project()
    owners = {
        "standards": project.standards,
        "requirements": project.requirements,
        "adr": project.adr,
        "context": project.context,
        "approved-plan": project.approved_plans,
        "rejected-plan": project.rejected_plans,
    }
    owner = owners[args.command]
    operation = getattr(owner, args.operation)
    arguments = vars(args).copy()
    del arguments["command"]
    del arguments["operation"]
    result = await operation(**arguments)
    if result is not None:
        sys.stdout.write(result)


def main():
    asyncio.run(run(build_parser().parse_args()))


if __name__ == "__main__":
    main()
