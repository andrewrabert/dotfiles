import os

from dotfiles import systemd


async def main():
    if os.environ["HOST_DOTFILES"] != "mars":
        return

    await systemd.Systemctl.enable("syncthing", user=True)
