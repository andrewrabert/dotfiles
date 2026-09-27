import shutil

from dotfiles import process


async def main(args):
    if shutil.which("git-sync"):
        await process.run("git-sync", "--build-cache")
