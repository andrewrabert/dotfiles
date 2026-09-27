import re
import shutil
import sys

from dotfiles import process

HELP = """usage:
    --rebase        rebase to newest Fedora version if available
    --help          show help and exit"""


def version_id():
    for line in open("/etc/os-release").read().splitlines():
        key, _, value = line.partition("=")
        if key == "VERSION_ID":
            return value.strip().strip("\"'")
    return ""


async def main(args):
    rebase = False
    for arg in args:
        if arg == "--rebase":
            rebase = True
        elif arg == "--help":
            print(HELP)
            return
        else:
            print("error: unknown argument(s)", file=sys.stderr)
            raise SystemExit(1)

    if not shutil.which("rpm-ostree"):
        return

    current = int(version_id())
    result = await process.run(
        "ostree",
        "--repo=/ostree/repo",
        "remote",
        "refs",
        "fedora",
        stdout=process.PIPE,
    )
    versions = []
    for line in result.stdout.decode().splitlines():
        fields = re.split("[:/]", line)
        if (
            len(fields) >= 5
            and fields[4] == "kinoite"
            and re.fullmatch("[0-9]+", fields[2])
        ):
            versions.append(int(fields[2]))
    latest = max(versions)

    if current < latest:
        if rebase:
            print(f"Rebasing from Fedora {current} to {latest}", flush=True)
            await process.run(
                "sudo",
                "rpm-ostree",
                "rebase",
                f"fedora:fedora/{latest}/x86_64/kinoite",
            )
            return
        print(
            f"WARNING: Fedora {latest} is available (currently on "
            f"{current}); pass --rebase to upgrade",
            file=sys.stderr,
        )

    await process.run("sudo", "rpm-ostree", "upgrade")
