import os
import pathlib
import shutil

from dotfiles import fs, process

SSHD_CONFIG = pathlib.Path(
    "/data/data/com.termux/files/usr/etc/ssh/sshd_config"
)
SSHD_CONFIG_TEXT = """PrintMotd no
PasswordAuthentication no
Subsystem sftp /data/data/com.termux/files/usr/libexec/sftp-server
"""


async def main(args):
    if not shutil.which("termux-info"):
        return

    home = pathlib.Path.home()
    dotfiles = fs.dotfiles()

    if os.path.realpath(home / ".termux") != f"{dotfiles}/termux":
        print("Linking configuration ...", flush=True)
        fs.delete(home / ".termux")
        (home / ".termux").symlink_to(dotfiles / "termux")

    if os.path.realpath(home / "bin") != f"{dotfiles}/termux/bin":
        print("Linking configuration ...", flush=True)
        fs.delete(home / "bin")
        (home / "bin").symlink_to(dotfiles / "termux/bin")

    await process.run("pkg", "install", "-y", "openssh", "termux-services")
    await process.run("sv-enable", "sshd")

    if SSHD_CONFIG.is_file():
        print("Linking sshd configuration ...")
        SSHD_CONFIG.write_text(SSHD_CONFIG_TEXT)

    # yes | termux-setup-storage
    fs.link(
        home / "notes",
        pathlib.Path("/storage/emulated/0/Syncthing/default/notes"),
    )
    fs.link(home / "syncthing", pathlib.Path("/storage/emulated/0/Syncthing"))
    fs.link(home / "download", pathlib.Path("/storage/emulated/0/Download"))

    # symlinking wont work
    await process.run(
        "rsync",
        "-a",
        "--delete",
        f"{dotfiles}/termux/shortcuts/",
        home / ".shortcuts",
    )

    await process.run("sh", "-c", "yes | pkg upgrade")
    await process.run("sh", "-c", "yes | pkg clean")

    (home / ".hushlogin").touch()
