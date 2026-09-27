from dotfiles import fs, nightly, process


async def install_completions(bertbox):
    dest = fs.dotfiles_local() / "zcomp" / "_bertbox"
    result = await process.run(
        bertbox, "completions", "zsh", stdout=process.PIPE
    )
    fs.write_atomic(dest, result.stdout)
    print(f"Installed: {dest}")


async def main(force):
    bertbox = await nightly.install(
        name="bertbox", repository="andrewrabert/tools", force=force
    )
    await install_completions(bertbox)
