import argparse
import shutil

from dotfiles import fs, nightly, process


async def install_completions(bertbox):
    dest = fs.dotfiles_local() / "zcomp" / "_bertbox"
    result = await process.run(
        bertbox, "completions", "zsh", stdout=process.PIPE
    )
    fs.write_atomic(dest, result.stdout)
    print(f"Installed: {dest}")


def parse_args(args):
    parser = argparse.ArgumentParser(prog="bertbox")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="skip the ETag check and reinstall",
    )
    return parser.parse_args(args)


async def main(args):
    if not shutil.which("bertbox"):
        return
    force = parse_args(args).force
    bertbox = await nightly.install(
        name="bertbox", repository="andrewrabert/tools", force=force
    )
    await install_completions(bertbox)
