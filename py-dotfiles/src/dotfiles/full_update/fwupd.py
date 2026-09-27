import shutil
import sys

from dotfiles import process


async def main(args):
    if shutil.which("fwupdmgr"):
        await process.run(
            "sudo", "fwupdmgr", "refresh", "--force", check=False
        )
        # tee to disable upload question
        result = await process.run(
            "sudo",
            "fwupdmgr",
            "get-updates",
            check=False,
            stdout=process.PIPE,
        )
        sys.stdout.buffer.write(result.stdout)
        sys.stdout.flush()
