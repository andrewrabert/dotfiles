import pathlib

from dotfiles import errors, process


class UV:
    @staticmethod
    async def find_python(version):
        result = await process.run(
            "uv",
            "python",
            "find",
            version,
            check=False,
            stdout=process.PIPE,
            stderr=process.DEVNULL,
        )
        match result.returncode:
            case 0:
                return pathlib.Path(result.stdout.decode().strip())
            case 2:
                return None
            case _:
                raise errors.ProcessError(result, f"uv python find {version}")

    @staticmethod
    async def install_python(version):
        await process.run("uv", "python", "install", version)
