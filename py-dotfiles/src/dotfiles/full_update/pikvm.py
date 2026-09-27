import os

from dotfiles import process

BLUE = "\033[0;34m"
RED = "\033[0;31m"
NC = "\033[0m"


async def main(args):
    if os.environ.get("HOST_DOTFILES", "") != "pikvm":
        return

    print(f"{BLUE}==> Updating all installed packages...{NC}", flush=True)
    await process.run("pacman", "-Syu", "--noconfirm", check=False)
    print()

    print(
        f"{BLUE}==> Checking for foreign packages (not in repos)...{NC}",
        flush=True,
    )
    await process.run("pacman", "-Qm", check=False)
    print()

    print(
        f"{BLUE}==> Checking for packages with missing dependencies...{NC}",
        flush=True,
    )
    await process.run("pacman", "-Dk", check=False)
    print()

    print(
        f"{BLUE}==> Checking if all installed packages are cached...{NC}",
        flush=True,
    )
    result = await process.run(
        "pacman", "-Qq", check=False, stdout=process.PIPE
    )
    packages = result.stdout.decode().split()
    result = await process.run(
        "pacman",
        "-Sp",
        *packages,
        check=False,
        stdout=process.PIPE,
        stderr=process.DEVNULL,
    )
    lines = result.stdout.decode().splitlines()
    if not any(not line.startswith("file://") for line in lines):
        print("All packages cached")
    else:
        print(f"{RED}Some packages not cached, downloading...{NC}", flush=True)
        result = await process.run(
            "pacman", "-Qq", check=False, stdout=process.PIPE
        )
        await process.run(
            "pacman",
            "-Sw",
            "--noconfirm",
            *result.stdout.decode().split(),
            check=False,
        )
    print()

    print(
        f"{BLUE}==> Pruning pacman cache to only installed packages...{NC}",
        flush=True,
    )
    await process.run("paccache", "--remove", "--keep", "1", check=False)
    print()

    print(
        f"{BLUE}==> Checking for .pacnew and .pacsave files...{NC}",
        flush=True,
    )
    await process.run(
        "find",
        "/etc",
        "-regextype",
        "posix-extended",
        "-regex",
        ".+\\.pac(new|save)",
        check=False,
        stderr=process.DEVNULL,
    )
    print()
