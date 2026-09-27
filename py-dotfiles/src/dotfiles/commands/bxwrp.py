import argparse
import shutil

import pydantic

from dotfiles import cache, errors, fs, process

REPOSITORY = "https://github.com/andrewrabert/bxwrp"

BRANCH = "main"


class Installed(pydantic.BaseModel):
    commit: str
    sha256: str


async def remote_head():
    result = await process.run(
        "git",
        "ls-remote",
        REPOSITORY,
        f"refs/heads/{BRANCH}",
        stdout=process.PIPE,
    )
    line = result.stdout.decode().split("\n", 1)[0].strip()
    if not line:
        raise errors.UserError(f"{REPOSITORY} has no branch {BRANCH}")
    return line.split()[0]


async def checkout(commit):
    source = fs.cache_dir() / "bxwrp-src"
    if not (source / ".git").is_dir():
        shutil.rmtree(source, ignore_errors=True)
        source.parent.mkdir(parents=True, exist_ok=True)
        await process.run("git", "clone", REPOSITORY, source)
    await process.run("git", "fetch", "origin", BRANCH, cwd=source)
    await process.run("git", "checkout", "--force", commit, cwd=source)
    await process.run("git", "clean", "-fdx", cwd=source)
    return source


async def build(source):
    print("Building...")
    await process.run("cargo", "build", "--release", cwd=source)
    binary = source / "target" / "release" / "bxwrp"
    if not binary.is_file():
        raise errors.UserError(f"build produced no binary at {binary}")
    return binary


def parse_args(args):
    parser = argparse.ArgumentParser(prog="bxwrp")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="skip the commit check and rebuild",
    )
    return parser.parse_args(args)


async def main(args):
    force = parse_args(args).force
    if not force and not shutil.which("bxwrp"):
        return
    local = fs.dotfiles_local()
    dest = local / "bxwrp" / "bin" / "bxwrp"
    symlink = local / "bin" / "bxwrp"
    installed_cache = cache.InstalledCache(
        path=fs.cache_dir() / "bxwrp-build.json", model=Installed
    )
    known = None if force else installed_cache.load(dest)

    commit = await remote_head()
    if known is not None and commit == known.commit:
        print("Already up to date")
        fs.link(symlink, dest)
        return

    source = await checkout(commit)
    binary = await build(source)
    fs.write_atomic(dest, binary.read_bytes(), mode=fs.EXECUTABLE)
    print(f"Installed: {dest}")
    fs.link(symlink, dest)
    installed = Installed(commit=commit, sha256=fs.sha256(dest))
    installed_cache.write(installed)
    print(f"Stored {installed.commit} for sha256 {installed.sha256}")
