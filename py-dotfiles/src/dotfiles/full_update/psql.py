import os
import pathlib
import shutil

from dotfiles import fs


async def main(args):
    target = pathlib.Path.home() / ".psqlrc"
    if shutil.which("psql"):
        source = fs.dotfiles() / "psql/.psqlrc"
        if os.path.realpath(target) != str(source):
            print("Linking configuration ...")
            fs.link(target, source)
    else:
        fs.delete(target)
