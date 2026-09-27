import argparse
import shutil

from dotfiles import fs, nightly
from dotfiles.bertbox import Bertbox
from dotfiles.commands import link_bin


async def install_completions():
    dest = fs.dotfiles_local() / "zcomp" / "_bertbox"
    fs.write_atomic(dest, await Bertbox.completions("zsh"))
    print(f"Installed: {dest}")


async def install_tools():
    dest = fs.dotfiles_local() / "bertbox" / "install"
    dest.mkdir(parents=True, exist_ok=True)
    await Bertbox.install(dest)
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
    force = parse_args(args).force
    if not force and not shutil.which("bertbox"):
        return
    await nightly.install(
        name="bertbox", repository="andrewrabert/tools", force=force
    )
    await install_completions()
    await install_tools()
    link_bin.main()
