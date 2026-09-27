"""Download and install the latest Jellium Desktop nightly.

With an SSH host, the download and extraction still happen locally and the
extracted artifact is pushed to the remote, where the install commands run
over SSH, so the remote never needs Python."""

import abc
import os
import pathlib
import plistlib
import shlex
import shutil
import tempfile
import zipfile

import yarl

from dotfiles import errors, nightly, process


async def run_bytes(*args, stderr=None):
    result = await process.run(*args, stdout=process.PIPE, stderr=stderr)
    return result.stdout


class Host(abc.ABC):
    @abc.abstractmethod
    async def run(self, *args, stderr=None):
        """Run a command on the host, returning its stdout."""

    @abc.abstractmethod
    async def read_bytes(self, path):
        pass

    @abc.abstractmethod
    async def push(self, local, dest_dir):
        """Copy a local file into `dest_dir` on the host, returning its path."""

    @abc.abstractmethod
    async def mkdtemp(self):
        pass

    @abc.abstractmethod
    async def home(self):
        pass

    @abc.abstractmethod
    async def env(self, name):
        """Return environment variable `name`, or None if unset/empty."""

    @abc.abstractmethod
    def path(self, value):
        pass

    @abc.abstractmethod
    async def read_text(self, path):
        """Return the file's stripped text, or None if it does not exist."""

    @abc.abstractmethod
    async def write_text(self, path, text):
        pass

    @abc.abstractmethod
    async def exists(self, path):
        pass

    @abc.abstractmethod
    async def is_dir(self, path):
        pass

    @abc.abstractmethod
    async def mkdir(self, path):
        pass

    @abc.abstractmethod
    async def rmtree(self, path):
        pass


class LocalHost(Host):
    async def run(self, *args, stderr=None):
        return (await run_bytes(*args, stderr=stderr)).decode()

    async def read_bytes(self, path):
        return pathlib.Path(path).read_bytes()

    async def push(self, local, dest_dir):
        return local

    async def mkdtemp(self):
        return pathlib.Path(tempfile.mkdtemp())

    async def home(self):
        return pathlib.Path.home()

    async def env(self, name):
        return os.environ.get(name) or None

    def path(self, value):
        return pathlib.Path(value)

    async def read_text(self, path):
        try:
            return pathlib.Path(path).read_text().strip()
        except FileNotFoundError:
            return None

    async def write_text(self, path, text):
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    async def exists(self, path):
        return pathlib.Path(path).exists()

    async def is_dir(self, path):
        return pathlib.Path(path).is_dir()

    async def mkdir(self, path):
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    async def rmtree(self, path):
        shutil.rmtree(path)


class SshHost(Host):
    def __init__(self, host):
        self._host = host
        self._env = {}

    async def _run_bytes(self, *args, stderr=None):
        # A tty is needed only for the sudo password prompt; it would mangle
        # binary output, so cat/other reads deliberately go without one.
        tty = bool(args) and str(args[0]) == "sudo"
        remote = shlex.join(str(arg) for arg in args)
        cmd = ["ssh"]
        if tty:
            cmd.append("-tt")
        cmd += [self._host, remote]
        return await run_bytes(*cmd, stderr=stderr)

    async def run(self, *args, stderr=None):
        return (await self._run_bytes(*args, stderr=stderr)).decode()

    async def read_bytes(self, path):
        return await self._run_bytes("cat", path)

    async def push(self, local, dest_dir):
        dest = pathlib.PurePosixPath(dest_dir) / local.name
        await process.run("scp", "-q", local, f"{self._host}:{dest}")
        return dest

    async def mkdtemp(self):
        return self.path((await self.run("mktemp", "-d")).strip())

    async def home(self):
        return self.path(await self.env("HOME"))

    async def env(self, name):
        if name not in self._env:
            try:
                value = await self.run(
                    "printenv", name, stderr=process.DEVNULL
                )
            except errors.ProcessError:
                value = ""
            self._env[name] = value.strip() or None
        return self._env[name]

    def path(self, value):
        return pathlib.PurePosixPath(value)

    async def read_text(self, path):
        try:
            return (
                await self.run("cat", path, stderr=process.DEVNULL)
            ).strip()
        except errors.ProcessError:
            return None

    async def write_text(self, path, text):
        await self.mkdir(pathlib.PurePosixPath(path).parent)
        await self.run("sh", "-c", 'printf %s "$1" > "$2"', "_", text, path)

    async def _test(self, flag, path):
        try:
            await self.run("test", flag, path)
            return True
        except errors.ProcessError:
            return False

    async def exists(self, path):
        return await self._test("-e", path)

    async def is_dir(self, path):
        return await self._test("-d", path)

    async def mkdir(self, path):
        await self.run("mkdir", "-p", path)

    async def rmtree(self, path):
        await self.run("rm", "-rf", path)


class Platform(abc.ABC):
    BASE = yarl.URL(
        "https://nightly.link/andrewrabert/jellium-desktop/workflows"
    )

    workflow: str
    archive_name: str
    key: str

    @property
    def url(self):
        return self.BASE / self.workflow / "main" / self.archive_name

    @abc.abstractmethod
    async def cache_dir(self, host):
        pass

    @abc.abstractmethod
    async def install(self, host, path):
        """Install the extracted artifact `path` on `host`."""


class FlatpakPlatform(Platform):
    workflow = "build-linux-flatpak"
    archive_name = "linux-flatpak-x86_64.zip"
    key = "flatpak"

    async def cache_dir(self, host):
        xdg = await host.env("XDG_CACHE_HOME")
        return host.path(xdg) if xdg else await host.home() / ".cache"

    async def install(self, host, path):
        if path.suffix != ".flatpak":
            raise errors.UserError(f"expected a .flatpak, got {path.name}")
        print("Installing...")
        await host.run(
            "flatpak",
            "install",
            "--user",
            "--noninteractive",
            "--or-update",
            path,
        )
        print("Installed")


class MacosPlatform(Platform):
    workflow = "build-macos"
    archive_name = "macos-arm64.zip"
    key = "macos"

    APP_NAME = "Jellium Desktop.app"
    applications = pathlib.PurePosixPath("/Applications")

    async def cache_dir(self, host):
        return await host.home() / "Library" / "Caches"

    @staticmethod
    async def _version(host, app):
        info = app / "Contents" / "Info.plist"
        plist = plistlib.loads(await host.read_bytes(info))
        short = plist.get("CFBundleShortVersionString")
        build = plist.get("CFBundleVersion")
        if short and build and short != build:
            return f"{short} ({build})"
        return short or build or "unknown"

    @staticmethod
    async def _is_quarantined(host, app):
        # com.apple.provenance is ignored - macOS re-adds it on launch and it
        # cannot be cleared, so it is not a meaningful signal.
        output = await host.run("xattr", "-r", app)
        return "com.apple.quarantine" in output

    async def install(self, host, path):
        if path.suffix != ".dmg":
            raise errors.UserError(f"expected a .dmg, got {path.name}")
        mount = path.parent / "mnt"
        await host.mkdir(mount)
        try:
            await host.run(
                "hdiutil", "attach", "-nobrowse", "-mountpoint", mount, path
            )
            app = mount / self.APP_NAME
            if not await host.is_dir(app):
                raise errors.UserError(
                    f"{self.APP_NAME} not found in {path.name}"
                )

            version = await self._version(host, app)
            print(f"Version: {version}")

            dest = self.applications / app.name
            installed = (
                await self._version(host, dest)
                if await host.exists(dest)
                else None
            )
            if installed == version:
                print(f"Already installed: {dest}")
            else:
                if installed is not None:
                    print(f"Replacing installed version {installed}")
                print(f"Installing to {dest}...")
                if await host.exists(dest):
                    await host.rmtree(dest)
                await host.run("ditto", app, dest)
                print(f"Installed: {dest}")
        finally:
            await host.run("hdiutil", "detach", mount)

        if await self._is_quarantined(host, dest):
            print("Clearing quarantine (sudo)...")
            await host.run(
                "sudo", "xattr", "-dr", "com.apple.quarantine", dest
            )


PLATFORMS = {
    platform.key: platform for platform in (FlatpakPlatform(), MacosPlatform())
}


class EtagCache:
    """Records the last-installed ETag on the target host, since it describes
    that host's state."""

    def __init__(self, host, platform):
        self._host = host
        self._platform = platform

    async def _path(self):
        base = await self._platform.cache_dir(self._host)
        return base / "jellium-desktop-nightly" / f"{self._platform.key}.etag"

    async def read(self):
        return await self._host.read_text(await self._path())

    async def write(self, etag):
        await self._host.write_text(await self._path(), etag)
        print(f"Stored etag {etag}")


async def main(platform, ssh):
    platform = PLATFORMS[platform]
    host = SshHost(ssh) if ssh else LocalHost()
    cache = EtagCache(host, platform)
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp)
        archive = work / platform.archive_name

        known = await cache.read()
        async with nightly.download(platform.url) as (etag, size, chunks):
            if etag == known:
                print("Already up to date")
                return
            with archive.open("wb") as handle:
                await nightly.receive(chunks, size, handle)

        print("Extracting...")
        with zipfile.ZipFile(archive) as zf:
            extracted = pathlib.Path(
                zf.extract(nightly.sole_member(zf), work / "extracted")
            )

        staging = await host.mkdtemp()
        try:
            path = await host.push(extracted, staging)
            await platform.install(host, path)
            await cache.write(etag)
        finally:
            await host.rmtree(staging)
