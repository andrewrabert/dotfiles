import argparse
import hashlib
import io
import platform
import tarfile

import httpx2
import pydantic
import yarl

from dotfiles import errors, fs, nightly

NAME = "uncomment"
OWNER = "polylint"
REPOSITORY = "uncomment"
RELEASES = yarl.URL(f"https://github.com/{OWNER}/{REPOSITORY}/releases")

TARGETS = {
    ("Linux", "x86_64"): "x86_64-unknown-linux-gnu",
    ("Linux", "aarch64"): "aarch64-unknown-linux-gnu",
    ("Darwin", "x86_64"): "x86_64-apple-darwin",
    ("Darwin", "arm64"): "aarch64-apple-darwin",
}


class ReleaseTag(pydantic.BaseModel):
    owner: str
    repository: str
    tag: str

    @classmethod
    def from_url(cls, url):
        """Parse https://github.com/OWNER/REPOSITORY/releases/tag/TAG."""
        url = yarl.URL(url)
        match url.parts:
            case ("/", owner, repository, "releases", "tag", *tag) if (
                url.host == "github.com" and all(tag)
            ):
                return cls(
                    owner=owner, repository=repository, tag="/".join(tag)
                )
        raise ValueError(f"not a GitHub release tag URL: {url}")


def parse_args(args):
    parser = argparse.ArgumentParser(prog=NAME)
    subparsers = parser.add_subparsers(dest="command", required=True)
    install_parser = subparsers.add_parser(
        "install", help="install the latest release"
    )
    install_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="skip the version check and reinstall",
    )
    subparsers.add_parser("uninstall", help="remove the installed release")
    subparsers.add_parser(
        "update", help="install the latest release if already installed"
    )
    return parser.parse_args(args)


def binary_path():
    return fs.dotfiles_local() / NAME / "bin" / NAME


def symlink_path():
    return fs.dotfiles_local() / "bin" / NAME


def detect_target():
    key = (platform.system(), platform.machine())
    if nightly.is_termux() or key not in TARGETS:
        raise errors.UserError(f"unsupported platform: {key[0]} {key[1]}")
    return TARGETS[key]


async def latest_tag(client):
    """Resolve the tag from the releases/latest redirect, avoiding the rate-limited API."""
    url = RELEASES / "latest"
    response = await client.head(str(url))
    location = response.headers.get("location")
    if response.status_code == 301:
        raise errors.UserError(
            f"{NAME} repository moved: {url} now redirects to {location};"
            " update OWNER and REPOSITORY"
        )
    if response.status_code != 302 or location is None:
        raise errors.UserError(
            f"could not resolve latest {NAME} release:"
            f" HTTP {response.status_code} from {url}"
        )
    try:
        release = ReleaseTag.from_url(location)
    except ValueError:
        raise errors.UserError(
            f"{NAME} has no published release: {url} redirects to {location}"
        ) from None
    if (release.owner, release.repository) != (OWNER, REPOSITORY):
        raise errors.UserError(
            f"{NAME} repository moved: {url} now redirects to {location};"
            " update OWNER and REPOSITORY"
        )
    return release.tag


async def expected_sha256(client, tag, asset):
    url = (
        RELEASES
        / "download"
        / tag
        / f"{NAME}_{tag.removeprefix('v')}_checksums.txt"
    )
    response = await client.get(str(url), follow_redirects=True)
    response.raise_for_status()
    for line in response.text.splitlines():
        digest, _, name = line.partition("  ")
        if name == asset:
            return digest
    raise errors.UserError(f"no checksum published for {asset}")


def extract_binary(archive):
    with tarfile.open(fileobj=archive) as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.rpartition("/")[2] == NAME:
                return tar.extractfile(member).read()
    raise errors.UserError(f"no {NAME} binary in download")


async def install(force):
    target = detect_target()
    dest = binary_path()
    symlink = symlink_path()
    version_file = fs.dotfiles_local() / NAME / ".installed-version"

    async with httpx2.AsyncClient() as client:
        tag = await latest_tag(client)
        installed = f"{tag} {target}"
        if (
            not force
            and dest.exists()
            and version_file.exists()
            and version_file.read_text().strip() == installed
        ):
            print(f"Already up to date ({tag})")
            fs.link(symlink, dest)
            return
        asset = f"{NAME}-{target}.tar.gz"
        expected = await expected_sha256(client, tag, asset)

    archive = io.BytesIO()
    async with nightly.download(RELEASES / "download" / tag / asset) as (
        _,
        size,
        chunks,
    ):
        await nightly.receive(chunks, size, archive)

    digest = hashlib.sha256(archive.getvalue()).hexdigest()
    if digest != expected:
        raise errors.UserError(f"{asset}: expected {expected}, got {digest}")

    print("Extracting...")
    archive.seek(0)
    fs.write_atomic(dest, extract_binary(archive), mode=fs.EXECUTABLE)
    print(f"Installed: {dest} ({tag})")
    fs.link(symlink, dest)
    version_file.write_text(installed + "\n")


async def update():
    if not binary_path().exists():
        print(f"{NAME} is not installed")
        return
    await install(force=False)


def uninstall():
    dest = binary_path()
    symlink = symlink_path()
    if symlink.is_symlink() and symlink.readlink() == dest:
        symlink.unlink()
    install_dir = fs.dotfiles_local() / NAME
    if not install_dir.exists():
        print(f"{NAME} is not installed")
        return
    fs.delete(install_dir)
    print(f"Removed: {install_dir}")


async def main_update(args):
    await update()


async def main(args):
    parsed = parse_args(args)
    match parsed.command:
        case "install":
            await install(parsed.force)
        case "uninstall":
            uninstall()
        case "update":
            await update()
