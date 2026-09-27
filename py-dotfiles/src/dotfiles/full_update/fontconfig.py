import os
import pathlib
import shutil

from dotfiles import fs


async def main(args):
    target = pathlib.Path.home() / ".config/fontconfig"
    if not shutil.which("fc-list"):
        fs.delete(target)
    else:
        source = fs.dotfiles() / "fontconfig"
        if os.path.realpath(target) != str(source):
            print("Linking configuration ...")
            fs.link(target, source)
