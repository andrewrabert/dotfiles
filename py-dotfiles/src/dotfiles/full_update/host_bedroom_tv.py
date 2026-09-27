import shutil

from dotfiles import fs, host, process


async def main(args):
    if host.name() != "bedroom-tv":
        return

    if not shutil.which("uv"):
        await process.run("bertbox", "full-update", "35-uv", "--force")
    await process.run(
        fs.dotfiles() / "scripts/install-jellium-desktop-nightly", "flatpak"
    )
