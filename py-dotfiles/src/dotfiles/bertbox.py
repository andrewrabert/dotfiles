from dotfiles import process


class Bertbox:
    @staticmethod
    async def full_update(*scripts, force=False):
        args = ["bertbox", "full-update", *scripts]
        if force:
            args.append("--force")
        await process.run(*args)
