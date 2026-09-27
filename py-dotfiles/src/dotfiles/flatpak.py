from dotfiles import process


class Flatpak:
    @staticmethod
    async def list_installed():
        result = await process.run(
            "flatpak",
            "list",
            "--app",
            "--columns=application",
            check=False,
            stdout=process.PIPE,
            stderr=process.DEVNULL,
        )
        if result.returncode:
            return set()
        return {
            line.strip()
            for line in result.stdout.decode().splitlines()
            if line.strip()
        }

    @staticmethod
    async def _permissions(app, kind):
        result = await process.run(
            "flatpak",
            "info",
            "--show-permissions",
            "--user",
            app,
            check=False,
            stdout=process.PIPE,
            stderr=process.DEVNULL,
        )
        if result.returncode:
            return set()
        values = set()
        for line in result.stdout.decode().splitlines():
            line = line.strip()
            if line.startswith(f"{kind}="):
                perms = line.split("=", 1)[1]
                values.update(p.strip() for p in perms.split(";") if p.strip())
        return values

    @staticmethod
    async def get_permissions(app):
        return await Flatpak._permissions(app, "filesystems")

    @staticmethod
    async def get_sockets(app):
        return await Flatpak._permissions(app, "sockets")

    @staticmethod
    async def install(remote, app):
        await process.run("flatpak", "install", "-y", "--user", remote, app)

    @staticmethod
    async def override_filesystem(app, path):
        await process.run(
            "flatpak", "override", "--user", app, f"--filesystem={path}"
        )

    @staticmethod
    async def override_socket(app, socket):
        await process.run(
            "flatpak", "override", "--user", app, f"--socket={socket}"
        )
