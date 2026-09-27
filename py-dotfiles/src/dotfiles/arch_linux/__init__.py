import os
import pathlib
import shutil

from dotfiles import fs, process

SRC = pathlib.Path(__file__).resolve().parents[2]

MAGENTA = "\033[1;35m"
YELLOW = "\033[1;33m"
RESET = "\033[0m"

KEY_ID = "952DF315E396E06A"
YAY_URL = "https://aur.archlinux.org/cgit/aur.git/snapshot/yay.tar.gz"
YAY_INSTALL = pathlib.Path("/tmp/yay-install")


def log(message):
    print(f"{MAGENTA}{message} ...{RESET}", flush=True)


def warn(message):
    print(f"{YELLOW}{message}{RESET}", flush=True)


async def main(args):
    if not shutil.which("pacman"):
        return

    env = {**os.environ, "PKGEXT": ".pkg.tar"}

    # Parse flags
    update_aur = "--aur" in args

    home = pathlib.Path.home()
    dotfiles = fs.dotfiles()
    pacman_config = home / ".config/pacman"
    if (
        not pacman_config.is_dir()
        or os.path.realpath(pacman_config) != f"{dotfiles}/pacman"
    ):
        fs.delete(pacman_config)
        fs.link(pacman_config, dotfiles / "pacman")

    result = await process.run(
        "pacman-key",
        "--list-keys",
        KEY_ID,
        check=False,
        env=env,
        stdout=process.DEVNULL,
        stderr=process.DEVNULL,
    )
    if result.returncode:
        log("Adding personal GPG key to pacman keyring")
        await process.run(
            "sudo", "pacman-key", "--add", "/etc/pacman.d/ar.asc", env=env
        )
        await process.run("sudo", "pacman-key", "--lsign-key", KEY_ID, env=env)

    if not shutil.which("yay"):
        YAY_INSTALL.mkdir()
        try:
            result = await process.run(
                "curl", YAY_URL, env=env, stdout=process.PIPE
            )
            await process.run(
                "tar",
                "-zxv",
                cwd=YAY_INSTALL,
                env=env,
                stdin=result.stdout,
            )
            await process.run(
                "makepkg",
                "-s",
                "--install",
                "--noconfirm",
                cwd=YAY_INSTALL / "yay",
                env=env,
            )
        finally:
            fs.delete(YAY_INSTALL)

    log("Updating repository packages")
    await process.run("sudo", "pacman", "-Syu", "--noconfirm", env=env)

    # Check for AUR updates
    if shutil.which("yay"):
        log("Checking for AUR updates")
        result = await process.run(
            "yay",
            "-Qua",
            check=False,
            env=env,
            stdout=process.PIPE,
            stderr=process.DEVNULL,
        )
        aur_package_list = sorted(result.stdout.decode().splitlines())
        aur_updates = len([line for line in aur_package_list if line])

        if aur_updates > 0:
            if update_aur:
                log(f"Updating {aur_updates} AUR packages")
                await process.run(
                    "yay", "-Sua", "--noconfirm", "--devel", env=env
                )
            else:
                warn(
                    f"⚠️  {aur_updates} AUR package(s) have updates available:"
                )
                print("\n".join(aur_package_list))
                warn("Run with --aur flag to update them.")
        else:
            log("No AUR updates available")

    if shutil.which("pkgfile"):
        log("Updating file cache")
        await process.run(
            "sudo", "pkgfile", "--update", env=env, stdout=process.DEVNULL
        )

    # TODO create prune script which keeps n-number of old versions of a
    # package
    if shutil.which("paccache"):
        log("Pruning package cache")
        await process.run(
            "paccache",
            "--remove",
            "--keep",
            "3",
            "--min-mtime",
            "30 days ago",
            env=env,
        )

    log("Locating .pac* files")
    await process.run(
        "sudo", "rm", "-f", "/etc/pacman.d/mirrorlist.pacnew", env=env
    )
    await process.run(
        "sudo",
        "find",
        "/etc",
        "-regextype",
        "posix-extended",
        "-regex",
        ".+\\.pac(new|save)",
        check=False,
        env=env,
        stderr=process.DEVNULL,
    )


async def main_99(args):
    if not pathlib.Path("/etc/arch-release").is_file():
        return
    result = await process.run(
        "pacman",
        "-Q",
        "pyalpm",
        stdout=process.DEVNULL,
        stderr=process.DEVNULL,
        check=False,
    )
    if result.returncode:
        await process.run("sudo", "pacman", "-S", "--noconfirm", "pyalpm")
    await process.run(
        "/usr/bin/python3",
        "-m",
        "dotfiles.arch_linux",
        *args,
        cwd=SRC,
    )
