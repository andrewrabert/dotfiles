from dotfiles import process


class Bertbox:
    @staticmethod
    async def completions(shell):
        result = await process.run(
            "bertbox", "completions", shell, stdout=process.PIPE
        )
        return result.stdout

    @staticmethod
    async def install(dest):
        await process.run("bertbox", "install", "--replace", dest)

    @staticmethod
    async def full_update(*scripts, force=False):
        args = ["bertbox", "full-update", *scripts]
        if force:
            args.append("--force")
        await process.run(*args)
