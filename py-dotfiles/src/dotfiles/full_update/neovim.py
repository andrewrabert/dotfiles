import os
import pathlib
import shutil

from dotfiles import fs, process


async def main(args):
    home = pathlib.Path.home()
    target = home / ".config/nvim"
    if not shutil.which("nvim"):
        fs.delete(target)
        fs.delete(home / ".cache/nvim")
        fs.delete(home / ".local/share/nvim")
        return

    source = fs.dotfiles() / "nvim"
    if os.path.realpath(target) != str(source):
        fs.link(target, source)

    await process.run("nvim", "--headless", "-c", "PackSync", "+qa")
    await process.run(
        "nvim",
        "--headless",
        "-c",
        "lua require('blink.cmp').build():wait(math.huge)",
        "+qa",
    )
