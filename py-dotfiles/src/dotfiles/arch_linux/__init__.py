import pathlib

if not pathlib.Path("/etc/arch-release").exists():
    raise ImportError("dotfiles.arch_linux requires Arch Linux")

from . import pacman

__all__ = ["pacman"]
