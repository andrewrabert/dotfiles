import shutil

from dotfiles import process

FLATHUB_URL = "https://flathub.org/repo/flathub.flatpakrepo"


async def main(args):
    if not shutil.which("flatpak"):
        return

    for install_type in ("--user", "--system"):
        print(f"flatak: {install_type}", flush=True)
        await process.run(
            "flatpak",
            "remote-add",
            install_type,
            "--if-not-exists",
            "flathub",
            FLATHUB_URL,
            check=False,
        )
        await process.run(
            "flatpak", "update", install_type, "--assumeyes", check=False
        )
        # flatpak repair --user
        await process.run(
            "flatpak",
            "uninstall",
            "--unused",
            install_type,
            "--assumeyes",
            check=False,
        )
