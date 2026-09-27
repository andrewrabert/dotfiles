import os
import pathlib
import platform
import shutil

from dotfiles import fs, process

REPO_URL = "https://github.com/google/jpegli.git"
BREW_DEPS = ["giflib", "jpeg-turbo", "libpng", "openexr", "zlib"]
PREFIX_DEPS = ["giflib", "jpeg-turbo", "libpng", "zlib"]


async def capture(*command, check=True, stderr=None):
    result = await process.run(
        *command, check=check, stdout=process.PIPE, stderr=stderr
    )
    return result


async def cpu_count():
    if shutil.which("nproc"):
        result = await capture("nproc")
        return result.stdout.decode().strip()
    probe = await process.run(
        "sysctl",
        "-n",
        "hw.logicalcpu",
        check=False,
        stdout=process.DEVNULL,
        stderr=process.DEVNULL,
    )
    if probe.returncode == 0:
        result = await capture("sysctl", "-n", "hw.logicalcpu")
        return result.stdout.decode().strip()
    return "4"


async def main(args):
    if platform.system() != "Darwin":
        return

    home = pathlib.Path.home()
    install_dir = home / ".local/share/jpegli"
    build_dir = install_dir / "build"
    bin_dir = home / ".local/bin"
    built_commit_file = build_dir / ".built-commit"

    if not (install_dir / ".git").is_dir():
        print("Cloning jpegli...", flush=True)
        await process.run(
            "git",
            "clone",
            "--depth",
            "1",
            "--recurse-submodules",
            "--shallow-submodules",
            REPO_URL,
            install_dir,
        )
    else:
        # pipeline status is cut's, so ls-remote failures are ignored
        result = await capture(
            "git",
            "-C",
            install_dir,
            "ls-remote",
            "origin",
            "main",
            check=False,
        )
        remote_commit = "\n".join(
            line.split("\t")[0] for line in result.stdout.decode().splitlines()
        )
        if (
            built_commit_file.is_file()
            and remote_commit == built_commit_file.read_text().rstrip("\n")
        ):
            print(f"jpegli: already up to date ({remote_commit})")
            return
        print("Updating jpegli...", flush=True)
        git = ["git", "-C", install_dir]
        await process.run(*git, "fetch", "--depth", "1", "origin", "main")
        await process.run(*git, "reset", "--hard", "origin/main")
        await process.run(
            *git,
            "submodule",
            "update",
            "--init",
            "--recursive",
            "--depth",
            "1",
            "--force",
        )

    result = await capture("git", "-C", install_dir, "rev-parse", "HEAD")
    current_commit = result.stdout.decode().strip()

    await process.run("brew", "install", *BREW_DEPS)

    prefixes = []
    for dep in PREFIX_DEPS:
        result = await capture("brew", "--prefix", dep)
        prefixes.append(result.stdout.decode().strip())
    env = {**os.environ, "CMAKE_PREFIX_PATH": ":".join(prefixes)}

    print(f"Building jpegli ({current_commit})...", flush=True)
    fs.delete(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    await process.run(
        "cmake",
        "-S",
        install_dir,
        "-B",
        build_dir,
        "-DCMAKE_BUILD_TYPE=Release",
        "-DBUILD_TESTING=OFF",
        env=env,
    )
    jobs = await cpu_count()
    await process.run("cmake", "--build", build_dir, "-j", jobs, env=env)

    bin_dir.mkdir(parents=True, exist_ok=True)
    fs.link(bin_dir / "cjpegli", build_dir / "tools/cjpegli")

    built_commit_file.write_text(f"{current_commit}\n")
    print(f"jpegli: built and installed cjpegli ({current_commit})")
