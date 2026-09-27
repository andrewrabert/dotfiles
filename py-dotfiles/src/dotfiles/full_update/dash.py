import os
import pathlib
import platform
import shutil

from dotfiles import fs


async def main(args):
    if platform.system() == "Darwin":
        return

    # mac (arm) seems to have bugs with heredocs occasionally
    # returning empty
    dash = shutil.which("dash")
    if not dash:
        return

    bin_dir = pathlib.Path.home() / ".local/bin"
    actual = os.path.realpath(dash)
    if actual == os.path.realpath(bin_dir / "sh"):
        return

    bin_dir.mkdir(parents=True, exist_ok=True)
    fs.link(bin_dir / "sh", pathlib.Path(actual))
