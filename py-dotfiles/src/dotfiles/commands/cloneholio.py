import argparse
import shutil

from dotfiles import nightly


def parse_args(args):
    parser = argparse.ArgumentParser(prog="cloneholio")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="skip the ETag check and reinstall",
    )
    return parser.parse_args(args)


async def main(args):
    force = parse_args(args).force
    if not force and not shutil.which("cloneholio"):
        return
    await nightly.install(
        name="cloneholio", repository="andrewrabert/cloneholio", force=force
    )
