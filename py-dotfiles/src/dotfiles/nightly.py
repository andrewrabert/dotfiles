import contextlib
import hashlib
import io
import os
import pathlib
import platform
import shutil
import zipfile

import httpx2
import pydantic
import rich.progress
import yarl

from dotfiles import cache, errors, fs, process

TARGETS = {
    ("Linux", "x86_64"): "x86_64-unknown-linux-musl",
    ("Linux", "aarch64"): "aarch64-unknown-linux-musl",
    ("Darwin", "x86_64"): "x86_64-apple-darwin",
    ("Darwin", "arm64"): "aarch64-apple-darwin",
}


class Installed(pydantic.BaseModel):
    etag: str
    sha256: str


def is_termux():
    return shutil.which("termux-info") is not None


def detect_target():
    key = (platform.system(), platform.machine())
    try:
        return TARGETS[key]
    except KeyError:
        raise errors.UserError(
            f"unsupported platform: {key[0]} {key[1]}"
        ) from None


async def install_termux(name, repository):
    owner, repo = repository.split("/")
    source = (
        pathlib.Path(os.environ["PREFIX"])
        / "etc"
        / "apt"
        / "sources.list.d"
        / f"{name}.list"
    )
    if not source.exists():
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            f"deb [trusted=yes] https://{owner}.github.io/{repo} stable main\n"
        )
    await process.run("pkg", "install", "-y", name)


def sole_member(archive):
    members = [m for m in archive.infolist() if not m.is_dir()]
    if len(members) != 1:
        raise errors.UserError(
            f"expected exactly one file in download, found {len(members)}"
        )
    return members[0]


@contextlib.asynccontextmanager
async def download(url):
    async with httpx2.AsyncClient() as client:
        async with client.stream(
            "GET", str(url), follow_redirects=True
        ) as response:
            response.raise_for_status()
            size = int(response.headers["content-length"])
            yield response.headers["etag"], size, response.aiter_bytes()


async def receive(chunks, size, handle):
    columns = (
        rich.progress.TextColumn("Downloading"),
        rich.progress.BarColumn(),
        rich.progress.DownloadColumn(),
        rich.progress.TransferSpeedColumn(),
        rich.progress.TimeRemainingColumn(),
    )
    with rich.progress.Progress(*columns) as progress:
        task = progress.add_task("download", total=size)
        async for chunk in chunks:
            handle.write(chunk)
            progress.update(task, advance=len(chunk))


async def install_nightly(name, repository, force):
    target = detect_target()
    local = fs.dotfiles_local()
    dest = local / name / "bin" / name
    symlink = local / "bin" / name
    installed_cache = cache.InstalledCache(
        path=fs.cache_dir() / f"{name}-nightly-{target}.json",
        model=Installed,
    )
    known = None if force else installed_cache.load(dest)
    url = (
        yarl.URL(f"https://nightly.link/{repository}/workflows/ci/main")
        / f"{name}-{target}.zip"
    )

    async with download(url) as (etag, size, chunks):
        if known is not None and etag == known.etag:
            print("Already up to date")
            fs.link(symlink, dest)
            return dest
        archive = io.BytesIO()
        await receive(chunks, size, archive)

    print("Extracting...")
    with zipfile.ZipFile(archive) as zf:
        binary = zf.read(sole_member(zf))

    fs.write_atomic(dest, binary, mode=fs.EXECUTABLE)
    print(f"Installed: {dest}")
    fs.link(symlink, dest)
    installed = Installed(etag=etag, sha256=hashlib.sha256(binary).hexdigest())
    installed_cache.write(installed)
    print(f"Stored {installed.etag} for sha256 {installed.sha256}")
    return dest


async def install(name, repository, force):
    if is_termux():
        await install_termux(name, repository)
        return name
    return await install_nightly(name, repository, force)
