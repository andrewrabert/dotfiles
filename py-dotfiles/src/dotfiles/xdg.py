import os
import pathlib

from dotfiles import process


def _base_dir(variable, default):
    value = os.environ.get(variable)
    return pathlib.Path(value) if value else pathlib.Path.home() / default


def cache_home():
    return _base_dir("XDG_CACHE_HOME", ".cache")


def config_home():
    return _base_dir("XDG_CONFIG_HOME", ".config")


def data_home():
    return _base_dir("XDG_DATA_HOME", ".local/share")


def runtime_dir():
    value = os.environ.get("XDG_RUNTIME_DIR")
    if value:
        return pathlib.Path(value)
    return pathlib.Path(f"/run/user/{os.getuid()}")


async def update_desktop_database():
    await process.run("update-desktop-database")
