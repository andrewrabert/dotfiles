import pydantic

from dotfiles import process


class Formula(pydantic.BaseModel):
    full_name: str


class Cask(pydantic.BaseModel):
    full_token: str


class Info(pydantic.BaseModel):
    formulae: list[Formula]
    casks: list[Cask]


class Homebrew:
    @staticmethod
    async def get_installed():
        result = await process.run(
            "brew", "info", "--json=v2", "--installed", stdout=process.PIPE
        )
        info = Info.model_validate_json(result.stdout)
        installed = set()
        names = [f.full_name for f in info.formulae]
        names.extend(c.full_token for c in info.casks)
        for name in names:
            if name in installed:
                raise RuntimeError(f"duplicate full_name {name}")
            installed.add(name)
        return installed

    @staticmethod
    async def install(packages):
        await process.run("brew", "install", "--", *packages)
