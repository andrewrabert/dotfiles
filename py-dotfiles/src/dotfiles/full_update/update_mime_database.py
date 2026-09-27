import os
import pathlib
import shutil
import sys

from dotfiles import fs, process


async def main(args):
    home = pathlib.Path.home()
    mimeapps = home / ".config/mimeapps.list"
    mime_dir = home / ".local/share/mime"
    packages = mime_dir / "packages"

    if shutil.which("update-mime-database"):
        fs.link(mimeapps, fs.dotfiles() / "mimeapps/mimeapps.list")

        packages_source = fs.dotfiles() / "shared-mime-info/packages"
        if packages.is_dir():
            if os.path.realpath(packages) != str(packages_source):
                print("error: unexpectedly exists", file=sys.stderr)
                raise SystemExit(1)
        else:
            mime_dir.mkdir(parents=True, exist_ok=True)
            fs.link(packages, packages_source)
        await process.run("update-mime-database", mime_dir, check=False)
    else:
        fs.delete(mimeapps)
        fs.delete(mime_dir)
