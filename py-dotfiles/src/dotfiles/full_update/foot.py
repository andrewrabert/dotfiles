import os
import pathlib
import shutil

from dotfiles import fs


async def main(args):
    target = pathlib.Path.home() / ".config/foot"
    if not shutil.which("foot"):
        fs.delete(target)
    else:
        source = fs.dotfiles() / "foot"
        if os.path.realpath(target) != str(source):
            print("Linking configuration ...")
            fs.link(target, source)
