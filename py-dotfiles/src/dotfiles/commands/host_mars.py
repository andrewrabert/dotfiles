from dotfiles import host, systemd


async def main():
    if host.name() != "mars":
        return

    await systemd.Systemctl.enable("syncthing", user=True)
