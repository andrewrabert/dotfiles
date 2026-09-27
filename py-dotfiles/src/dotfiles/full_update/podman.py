import os
import pathlib
import shutil

from dotfiles import fs


async def main(args):
    if not shutil.which("podman"):
        return

    source = fs.dotfiles() / "podman/registries.conf"
    config_dir = pathlib.Path.home() / ".config/containers"
    target = config_dir / "registries.conf"
    if os.path.realpath(target) != str(source):
        config_dir.mkdir(parents=True, exist_ok=True)
        target.symlink_to(source)
