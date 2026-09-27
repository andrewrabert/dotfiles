import os
import pathlib

from dotfiles import fs, host, process


async def main(args):
    if host.name() != "sol":
        return

    home = pathlib.Path.home()
    target = home / ".config/systemd"
    source = fs.dotfiles() / "systemd"
    if not target.is_dir() or os.path.realpath(target) != str(source):
        fs.link(target, source)

    await process.run("git-auto-update", home / "src/nullsum/ar/sol-docker")
    await process.run("sol-docker", "pull")
    await process.run("sol-repotool", "update")

    print(":: Generating NVIDIA CDI spec")
    await process.run(
        "sudo",
        "nvidia-ctk",
        "cdi",
        "generate",
        "--output=/etc/cdi/nvidia.yaml",
    )
