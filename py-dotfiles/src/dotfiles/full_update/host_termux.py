import shutil

from dotfiles import process


async def main(args):
    # hostname is not set to anything useful
    if not shutil.which("termux-info"):
        return
    if not shutil.which("ty"):
        await process.run("pkg", "install", "ty")
