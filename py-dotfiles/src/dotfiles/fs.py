import hashlib
import os
import pathlib
import platform
import shutil
import tempfile

from dotfiles import errors

EXECUTABLE = 0o755


def dotfiles():
    value = os.environ.get("DOTFILES")
    if not value:
        raise errors.UserError("DOTFILES is not set")
    return pathlib.Path(value)


def dotfiles_local():
    return dotfiles() / ".local"


def cache_dir():
    if platform.system() == "Darwin":
        return pathlib.Path.home() / "Library" / "Caches"
    xdg = os.environ.get("XDG_CACHE_HOME")
    return pathlib.Path(xdg) if xdg else pathlib.Path.home() / ".cache"


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def delete(path):
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)


def link(path, target):
    if path.is_symlink() and path.readlink() == target:
        return
    delete(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.symlink_to(target)


def write_atomic(path, data, mode=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        delete=False, dir=path.parent, prefix=f".{path.name}."
    ) as handle:
        temp_path = pathlib.Path(handle.name)
        try:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
            if mode is not None:
                temp_path.chmod(mode)
            temp_path.replace(path)
        finally:
            temp_path.unlink(missing_ok=True)
