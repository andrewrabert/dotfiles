import shutil
import sys

from dotfiles import process

HELP = """usage:
    -f, --force     install/update pi coding agent with npm
    --help          show help and exit"""


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

    if force:
        print("Updating pi coding agent...", flush=True)
        await process.run(
            "npm",
            "install",
            "-g",
            "--ignore-scripts",
            "@earendil-works/pi-coding-agent",
        )

    if shutil.which("pi"):
        await process.run("pi", "update", "--self", check=False)
        await process.run("pi", "update", "--extensions")
        await process.run("pi", "update", "--models")
