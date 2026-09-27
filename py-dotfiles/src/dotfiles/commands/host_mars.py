from dotfiles import host, systemd


async def main(args):
    if host.name() != "mars":
        return

    await systemd.Systemctl.enable("syncthing", user=True)
