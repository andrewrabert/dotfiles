import os
import pathlib
import platform
import shutil

from dotfiles import fs

MACOS_APP = pathlib.Path("/Applications/Ghostty.app")


async def main(args):
    source = fs.dotfiles() / "ghostty"
    darwin = platform.system() == "Darwin"

    if darwin:
        target = (
            pathlib.Path.home()
            / "Library/Application Support/com.mitchellh.ghostty"
        )
        installed = MACOS_APP.is_dir()
    else:
        target = pathlib.Path.home() / ".config/ghostty"
        installed = shutil.which("ghostty") is not None

    if not installed:
        fs.delete(target)
        return

    if os.path.realpath(target) != str(source):
        print("Linking configuration ...")
        fs.link(target, source)

    config_local = source / "config-local"
    if darwin:
        config_local.write_text("config-file = config-macos\n")
    else:
        config_local.unlink(missing_ok=True)
