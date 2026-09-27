import os
import pathlib
import shutil

from dotfiles import fs


async def main(args):
    target = pathlib.Path.home() / ".tmux.conf"
    if not shutil.which("tmux"):
        fs.delete(target)
    else:
        source = fs.dotfiles() / "tmux/.tmux.conf"
        if os.path.realpath(target) != str(source):
            print("Linking configuration ...")
            fs.delete(target)
            target.symlink_to(source)
