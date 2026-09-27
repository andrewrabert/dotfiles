import platform

if platform.system() != "Darwin":
    raise ImportError("dotfiles.macos requires macOS")

from . import homebrew, packages

__all__ = ["homebrew", "packages"]
