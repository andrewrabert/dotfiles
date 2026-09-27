import os
import pathlib
import shutil

from dotfiles import fs


async def main(args):
    target = pathlib.Path.home() / ".config/yazi"
    if not shutil.which("yazi"):
        fs.delete(target)
    else:
        source = fs.dotfiles() / "yazi"
        if os.path.realpath(target) != str(source):
            print("Linking configuration ...")
            fs.delete(target)
            target.symlink_to(source)
