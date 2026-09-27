import pathlib
import platform
import shutil
import tarfile
import tempfile

import httpx2
import pydantic

from dotfiles import errors, fs, host

REPO = "andrewrabert/zoekt-simple"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"

ARCH_MAP = {
    "x86_64": "amd64",
    "aarch64": "arm64",
    "arm64": "arm64",
}


class Asset(pydantic.BaseModel):
    name: str
    browser_download_url: str


class Release(pydantic.BaseModel):
    tag_name: str
    assets: list[Asset]


def detect_platform():
    os_name = platform.system().lower()
    if os_name not in ("linux", "darwin"):
        raise errors.UserError(f"unsupported OS: {os_name}")

    machine = platform.machine()
    arch = ARCH_MAP.get(machine)
    if not arch:
        raise errors.UserError(f"unsupported architecture: {machine}")

    return os_name, arch


async def main(args):
    install_dir = fs.dotfiles_local() / "zoekt-simple"
    if host.name() != "aweber":
        fs.delete(install_dir)
        return
    bin_dir = install_dir / "bin"
    version_file = install_dir / ".installed-version"

    response = httpx2.get(API_URL, follow_redirects=True)
    release = Release.model_validate_json(response.content)
    tag = release.tag_name

    os_name, arch = detect_platform()
    asset_name = f"zoekt-{os_name}-{arch}.tar.gz"

    if version_file.exists() and version_file.read_text().strip() == tag:
        print(f"zoekt-simple: already up to date ({tag}, {os_name}-{arch})")
        return

    asset_url = None
    for asset in release.assets:
        if asset.name == asset_name:
            asset_url = asset.browser_download_url
            break

    if not asset_url:
        raise errors.UserError(f"no release asset found for {asset_name}")

    print(f"zoekt-simple: downloading {tag} ({asset_name})...")
    install_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tmp_path = pathlib.Path(tmp.name)
        try:
            with httpx2.stream(
                "GET", asset_url, follow_redirects=True
            ) as response:
                for chunk in response.iter_bytes():
                    tmp.write(chunk)
            tmp.flush()

            if bin_dir.exists():
                shutil.rmtree(bin_dir)
            bin_dir.mkdir(parents=True)

            with tarfile.open(tmp_path) as tar:
                for member in tar.getmembers():
                    if member.isfile():
                        member.name = pathlib.PurePosixPath(member.name).name
                        tar.extract(member, path=bin_dir)
                        (bin_dir / member.name).chmod(fs.EXECUTABLE)
        finally:
            tmp_path.unlink(missing_ok=True)

    version_file.write_text(tag)
    print(f"zoekt-simple: installed {tag} ({os_name}-{arch})")
