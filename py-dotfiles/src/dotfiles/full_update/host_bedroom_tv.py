import shutil

from dotfiles import fs, host, process
from dotfiles.bertbox import Bertbox


async def main(args):
    if host.name() != "bedroom-tv":
        return

    if not shutil.which("uv"):
        await Bertbox.full_update("35-uv", force=True)
    await process.run(
        fs.dotfiles() / "scripts/install-jellium-desktop-nightly", "flatpak"
    )
