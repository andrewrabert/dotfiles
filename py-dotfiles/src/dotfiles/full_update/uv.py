import os
import pathlib
import shutil
import sys
import tempfile

from dotfiles import fs, process

HELP = """usage:
    -f, --force     force installation
    --uv-sh         install uv via astral.sh even if pacman or brew is present
    --help          show help and exit"""

UV_URL = "https://astral.sh/uv/install.sh"


async def install_uv_sh(env):
    fd, temp_name = tempfile.mkstemp()
    os.close(fd)
    temp_file = pathlib.Path(temp_name)
    try:
        print(f"Installing uv from {UV_URL}")
        with temp_file.open("wb") as handle:
            await process.run("curl", "-LsSf", UV_URL, stdout=handle)
        temp_file.chmod(0o755)
        await process.run(
            temp_file, env={**env, "INSTALLER_NO_MODIFY_PATH": "1"}
        )
        print("Successfully installed uv")
        home = pathlib.Path.home()
        env["PATH"] = f"{home}/.local/bin:{env.get('PATH', '')}"
    finally:
        temp_file.unlink(missing_ok=True)


async def main(args):
    force = False
    uv_sh = False
    for arg in args:
        if arg in ("-f", "--force"):
            force = True
        elif arg == "--uv-sh":
            uv_sh = True
        elif arg == "--help":
            print(HELP)
            return
        else:
            print("error: unknown argument(s)", file=sys.stderr)
            raise SystemExit(1)

    if not force and not shutil.which("uv"):
        return

    env = {**os.environ}
    if not shutil.which("uv"):
        if not uv_sh and shutil.which("pacman"):
            print("Installing uv via pacman")
            await process.run(
                "sudo", "pacman", "-S", "--needed", "--noconfirm", "uv"
            )
        elif not uv_sh and shutil.which("brew"):
            print("Installing uv via brew")
            await process.run("brew", "install", "uv")
        else:
            await install_uv_sh(env)

    print("Upgrading all uv tool installs...", flush=True)
    await process.run("uv", "tool", "upgrade", "--all", env=env)

    print("Updating uv PEP 723 scripts in dotfiles...", flush=True)
    await process.run(
        "uv-update-all", fs.dotfiles() / ".local/bin", check=False, env=env
    )
