import shutil

if not shutil.which("plasmashell"):
    raise ImportError("dotfiles.kde requires KDE Plasma")

from . import color_schemes, kconfig, settings

__all__ = ["color_schemes", "kconfig", "settings"]
