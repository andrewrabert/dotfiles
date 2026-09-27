from dotfiles import process


class Systemctl:
    @staticmethod
    async def is_enabled(name, user=False):
        result = await process.run(
            "systemctl",
            "--user" if user else "--system",
            "show",
            "--property=UnitFileState",
            "--",
            name,
            stdout=process.PIPE,
        )
        state = result.stdout.decode().strip()
        match state:
            case "UnitFileState=enabled":
                return True
            case "UnitFileState=disabled":
                return False
            case _:
                raise RuntimeError(f"Unexpected UnitFileState: {state}")

    @staticmethod
    async def enable(name, now=False, user=False):
        if await Systemctl.is_enabled(name, user=user):
            return
        print(f"Enabling unit {name} (user={user}) (now={now})")
        args = []
        if not user:
            args.append("sudo")
        args.extend(["systemctl", "--user" if user else "--system", "enable"])
        if now:
            args.append("--now")
        args.extend(["--", name])
        await process.run(*args)
