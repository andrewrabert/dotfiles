import os
import pathlib
import sys

from dotfiles import process

HELP = """usage:
    -f, --force     force installation
    --help          show help and exit"""

NVM_SCRIPT = """set -e
. ./nvm.sh
nvm install node --latest-npm
npm install -g npm@latest
NVM_SYMLINK_CURRENT=true nvm use node
"""


async def main(args):
    force = False
    for arg in args:
        if arg in ("-f", "--force"):
            force = True
        elif arg == "--help":
            print(HELP)
            return
        else:
            print("error: unknown argument(s)", file=sys.stderr)
            raise SystemExit(1)

    data_dir = pathlib.Path(
        os.environ.get("XDG_DATA_DIR") or pathlib.Path.home() / ".local/share"
    )
    install_dir = data_dir / "nvm"

    if not force and not install_dir.is_dir():
        return

    if not install_dir.is_dir():
        data_dir.mkdir(parents=True, exist_ok=True)
        await process.run(
            "git",
            "clone",
            "https://github.com/creationix/nvm",
            install_dir,
            stdout=process.DEVNULL,
        )
    else:
        await process.run("git", "clean", "-fd", cwd=install_dir)
        await process.run("git", "pull", cwd=install_dir)

    await process.run("sh", "-c", NVM_SCRIPT, cwd=install_dir)
