import pathlib
import shutil

from dotfiles import fs, host, process


async def main(args):
    home = pathlib.Path.home()
    if not shutil.which("zsh"):
        fs.delete(home / ".zshenv")
        fs.delete(home / ".zshrc")
        fs.delete(home / ".zlogin")
    else:
        dotfiles = fs.dotfiles()
        fs.link(home / ".zshenv", dotfiles / "zsh/.zshenv")
        fs.link(home / ".zshrc", dotfiles / "zsh/.zshrc")

        hostname = host.name()
        zlogin = dotfiles / "zsh/hosts" / hostname / ".zlogin"
        if hostname and zlogin.is_file():
            fs.link(home / ".zlogin", zlogin)
        (home / ".zcompdump").unlink(missing_ok=True)
        await process.run("zsh", "-ic", "echo -n")
