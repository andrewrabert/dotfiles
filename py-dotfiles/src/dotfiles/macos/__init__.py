import pathlib
import platform

from dotfiles import process


async def main(args):
    if platform.system() != "Darwin":
        return

    await process.run("brew", "update")
    await process.run("brew", "upgrade")

    (pathlib.Path.home() / ".hushlogin").touch()
