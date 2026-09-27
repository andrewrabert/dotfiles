import os
import pathlib
import shutil
import sys
import tempfile

from dotfiles import fs, process

HELP = """usage:
    -f, --force     force installation
    --rustup-sh     install rustup via sh.rustup.rs even if pacman is present
    --help          show help and exit"""

RUSTUP_URL = "https://sh.rustup.rs"


async def install_rustup_sh(env):
    cargo_home = pathlib.Path.home() / ".cargo"
    env["CARGO_HOME"] = str(cargo_home)
    fd, temp_name = tempfile.mkstemp()
    os.close(fd)
    temp_file = pathlib.Path(temp_name)
    try:
        print(f"Installing rustup from {RUSTUP_URL}")
        with temp_file.open("wb") as handle:
            await process.run("curl", RUSTUP_URL, stdout=handle, env=env)
        temp_file.chmod(0o755)
        await process.run(
            temp_file,
            "-y",
            "--no-modify-path",
            env={**env, "RUSTUP_INIT_SKIP_PATH_CHECK": "yes"},
        )
        print("Successfully installed rustup")
        env["PATH"] = f"{cargo_home}/bin:{env.get('PATH', '')}"
    finally:
        temp_file.unlink(missing_ok=True)


async def main(args):
    force = False
    rustup_sh = False
    for arg in args:
        if arg in ("-f", "--force"):
            force = True
        elif arg == "--rustup-sh":
            rustup_sh = True
        elif arg == "--help":
            print(HELP)
            return
        else:
            print("error: unknown argument(s)", file=sys.stderr)
            raise SystemExit(1)

    if not force and not shutil.which("rustup"):
        return

    env = {**os.environ}
    if not shutil.which("rustup"):
        if not rustup_sh and shutil.which("pacman"):
            print("Installing rustup via pacman")
            await process.run(
                "sudo", "pacman", "-S", "--needed", "--noconfirm", "rustup"
            )
        else:
            await install_rustup_sh(env)

    result = await process.run(
        "rustup",
        "toolchain",
        "list",
        check=False,
        env=env,
        stdout=process.PIPE,
    )
    lines = result.stdout.decode().splitlines()
    if not any(line.startswith("stable-") for line in lines):
        print("Installing toolchain: stable")
        await process.run("rustup", "toolchain", "install", "stable", env=env)

    result = await process.run(
        "rustup",
        "component",
        "list",
        "--installed",
        check=False,
        env=env,
        stdout=process.PIPE,
    )
    lines = result.stdout.decode().splitlines()
    if not any(line.startswith("rust-analyzer-") for line in lines):
        print("Installing component: rust-analyzer")
        await process.run(
            "rustup", "component", "add", "rust-analyzer", env=env
        )
    await process.run("rustup", "update", env=env)

    cargo_home = pathlib.Path(
        env.get("CARGO_HOME") or pathlib.Path.home() / ".cargo"
    )
    cargo_config = cargo_home / "config.toml"
    cargo_config_source = fs.dotfiles() / "cargo/config.toml"
    cargo_home.mkdir(parents=True, exist_ok=True)
    if os.path.realpath(cargo_config) != str(cargo_config_source):
        print("Linking cargo config ...")
        cargo_config.unlink(missing_ok=True)
        cargo_config.symlink_to(cargo_config_source)
