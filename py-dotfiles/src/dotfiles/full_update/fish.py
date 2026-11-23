import pathlib
import shutil

from dotfiles import fs


async def main(args):
    config_dir = pathlib.Path.home() / ".config/fish"
    link = config_dir / "conf.d/dotfiles.fish"
    target = fs.dotfiles() / "fish/dotfiles.fish"

    # ~/.config/fish used to link to $DOTFILES/fish
    if config_dir.is_symlink() and config_dir.readlink() == target.parent:
        config_dir.unlink()

    if shutil.which("fish"):
        fs.link(link, target)
    elif link.is_symlink() and link.readlink() == target:
        link.unlink()
