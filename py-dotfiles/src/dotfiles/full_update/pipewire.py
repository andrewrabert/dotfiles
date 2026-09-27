import os
import pathlib
import shutil

from dotfiles import fs


async def main(args):
    target = pathlib.Path.home() / ".config/pipewire"
    if not shutil.which("pipewire"):
        fs.delete(target)
    else:
        source = fs.dotfiles() / "pipewire"
        if os.path.realpath(target) != str(source):
            print("Linking configuration ...")
            fs.link(target, source)
