import os
import pathlib
import shutil

from dotfiles import fs


async def main(args):
    target = pathlib.Path.home() / ".config/zed"
    # zeditor - Arch Linux package
    # zed     - "Install CLI" from Zed on macos
    if not shutil.which("zeditor") and not shutil.which("zed"):
        fs.delete(target)
        return

    source = fs.dotfiles() / "zed"
    if os.path.realpath(target) != str(source):
        fs.link(target, source)
