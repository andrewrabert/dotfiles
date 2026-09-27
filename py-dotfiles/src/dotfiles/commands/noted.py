from dotfiles import nightly


async def main(force):
    await nightly.install(
        name="noted", repository="andrewrabert/noted", force=force
    )
