import asyncio
import dataclasses
import shlex

from dotfiles import errors

PIPE = asyncio.subprocess.PIPE
DEVNULL = asyncio.subprocess.DEVNULL


@dataclasses.dataclass
class Result:
    returncode: int | None
    stdout: bytes | None


async def run(
    *command, check=True, cwd=None, env=None, stdout=None, stderr=None
):
    proc = await asyncio.create_subprocess_exec(
        *command,
        cwd=cwd,
        env=env,
        stdout=stdout,
        stderr=stderr,
    )
    out, _ = await proc.communicate()
    if check and proc.returncode:
        raise errors.ProcessError(
            proc, shlex.join(str(part) for part in command)
        )
    return Result(returncode=proc.returncode, stdout=out)
