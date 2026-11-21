import shutil

from dotfiles import host, process
from dotfiles.bertbox import Bertbox


async def main(args):
    if host.name() != "bedroom-tv":
        return

    if not shutil.which("uv"):
        await Bertbox.full_update("35-uv", force=True)
    await process.run("bertbox", "install", "--flatpak", "jellium-desktop")
