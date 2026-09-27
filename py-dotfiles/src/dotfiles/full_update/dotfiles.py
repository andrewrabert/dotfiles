import os
import shutil
import sys

from dotfiles import fs, process
from dotfiles.commands import link_bin

USAGE = """usage: [OPTION]
  --no-push     disable git push
  --system      also install system files
  -h, --help
  --verbose"""

MAGENTA = "\033[1;35m"
RED = "\033[1;31m"
YELLOW = "\033[1;34m"
RESET = "\033[0m"
BOLD = "\033[1m"


async def sudo_test(flag, path):
    result = await process.run("sudo", "test", flag, path, check=False)
    return result.returncode == 0


def find_files(root):
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            if os.path.isfile(path) and not os.path.islink(path):
                yield path


async def update_non_user(dotfiles_root, tag, verbose):
    backup_root = f"{dotfiles_root}/non-user/{tag}"
    if not os.path.isdir(backup_root):
        return
    for source_file in find_files(backup_root):
        target = source_file.removeprefix(backup_root)
        if await sudo_test("-L", target) and not os.path.islink(source_file):
            print(
                f"{YELLOW}Warning: {target} is a symlink but source is not, "
                f"skipping{RESET}",
                flush=True,
            )
            continue
        if os.path.islink(source_file) and await sudo_test("-L", target):
            source_link = os.readlink(source_file)
            result = await process.run(
                "sudo", "readlink", target, stdout=process.PIPE
            )
            target_link = result.stdout.decode().rstrip("\n")
            if source_link != target_link:
                print("Syncing", target, flush=True)
                await process.run(
                    "sudo", "mkdir", "-p", os.path.dirname(target)
                )
                await process.run("sudo", "cp", "-P", source_file, target)
            elif verbose:
                print("Found", tag, target, flush=True)
        elif await sudo_test("-f", target) or tag != "common":
            same = False
            if await sudo_test("-f", target):
                result = await process.run(
                    "sudo",
                    "diff",
                    source_file,
                    target,
                    check=False,
                    stdout=process.DEVNULL,
                    stderr=process.DEVNULL,
                )
                same = result.returncode == 0
            if not same:
                print("Syncing", target, flush=True)
                await process.run(
                    "sudo", "mkdir", "-p", os.path.dirname(target)
                )
                await process.run("sudo", "cp", source_file, target)
            elif verbose:
                print("Found", tag, target, flush=True)


async def update_repo(name, dotfiles_root, options):
    print(f"{MAGENTA}Updating {name} ({dotfiles_root})...{RESET}", flush=True)
    if not options["no_pull"]:
        no_push = ["--no-push"] if options["no_push"] else []
        await process.run("git", "auto-update", *no_push, dotfiles_root)

    if options["install_system"]:
        print(
            f"{MAGENTA}Updating non-user files {name} "
            f"({dotfiles_root})...{RESET}",
            flush=True,
        )
        if shutil.which("sudo"):
            await update_non_user(
                dotfiles_root, options["host"], options["verbose"]
            )
            if shutil.which("pacman"):
                await update_non_user(
                    dotfiles_root, "_archlinux", options["verbose"]
                )


async def main(args):
    dotfiles = str(fs.dotfiles())
    options = {
        "verbose": False,
        "install_system": False,
        "no_push": False,
        "no_pull": False,
    }
    result = await process.run(
        "git",
        "-C",
        dotfiles,
        "remote",
        "get-url",
        "origin",
        stdout=process.PIPE,
    )
    if result.stdout.decode().strip().startswith("https://"):
        options["no_push"] = True

    host_dotfiles = os.environ.get("HOST_DOTFILES", "")
    if not host_dotfiles:
        raise SystemExit(1)
    options["host"] = host_dotfiles

    for arg in args:
        if arg in ("-h", "--help"):
            print(USAGE)
            return
        elif arg == "--no-pull":
            options["no_pull"] = True
        elif arg == "--no-push":
            options["no_push"] = True
        elif arg == "-v":
            options["verbose"] = True
        elif arg == "--system":
            options["install_system"] = True
        else:
            print(USAGE, file=sys.stderr)
            print("error: unrecognized arguments", file=sys.stderr)
            raise SystemExit(1)

    if not shutil.which("git-auto-update"):
        link_bin.main()

    await update_repo("DOTFILES", dotfiles, options)

    for name in sorted(os.environ):
        if name.startswith("DOTFILES_"):
            await update_repo(name, os.environ[name], options)

    link_bin.main()
