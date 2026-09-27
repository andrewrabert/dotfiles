import os
import pathlib
import shutil

from dotfiles import fs


async def main(args):
    target = pathlib.Path.home() / ".config/mpv"
    if not shutil.which("mpv"):
        fs.delete(target)
    else:
        source = fs.dotfiles() / "mpv"
        if os.path.realpath(target) != str(source):
            print("Linking configuration ...")
            fs.link(target, source)
