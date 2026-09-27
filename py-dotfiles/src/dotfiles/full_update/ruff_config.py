import os
import pathlib
import shutil

from dotfiles import fs


async def main(args):
    target = pathlib.Path.home() / ".config/ruff"
    if not shutil.which("ruff"):
        fs.delete(target)
    else:
        source = fs.dotfiles() / "ruff"
        if os.path.realpath(target) != str(source):
            print("Linking configuration ...")
            fs.link(target, source)
