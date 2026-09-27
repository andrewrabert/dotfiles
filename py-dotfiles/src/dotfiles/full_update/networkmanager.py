import grp
import os
import pathlib
import pwd
import shutil

from dotfiles import fs, process

TARGET_DIR = pathlib.Path("/etc/NetworkManager/dispatcher.d")


def owner(path):
    info = os.stat(path)
    user = pwd.getpwuid(info.st_uid).pw_name
    group = grp.getgrgid(info.st_gid).gr_name
    return f"{user}:{group}"


async def main(args):
    if not shutil.which("nmcli"):
        return

    source_dir = fs.dotfiles() / "networkmanager/dispatcher.d"
    for source_file in sorted(source_dir.glob("*")):
        target_file = TARGET_DIR / source_file.name
        if (
            not target_file.is_file()
            or (
                await process.run(
                    "diff",
                    source_file,
                    target_file,
                    check=False,
                    stdout=process.DEVNULL,
                    stderr=process.DEVNULL,
                )
            ).returncode
        ):
            print("Syncing", target_file, flush=True)
            await process.run("sudo", "mkdir", "-p", target_file.parent)
            await process.run("sudo", "cp", source_file, target_file)
        if owner(target_file) != "root:root":
            await process.run("sudo", "chown", "root:root", target_file)
