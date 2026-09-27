import os
import pathlib

from dotfiles import fs, process

REPOS = ["tinted-shell"]


async def main(args):
    data_dir = pathlib.Path(
        os.environ.get("XDG_DATA_DIR") or pathlib.Path.home() / ".local/share"
    )
    base_dir = data_dir / "tinted-theming"

    base_dir.mkdir(parents=True, exist_ok=True)

    for repo in REPOS:
        repo_dir = base_dir / repo
        if not repo_dir.is_dir():
            await process.run(
                "git",
                "clone",
                f"https://github.com/tinted-theming/{repo}",
                repo_dir,
                stdout=process.DEVNULL,
            )
        else:
            await process.run("git", "clean", "-xdff", cwd=repo_dir)
            await process.run("git", "reset", "--hard", "-q", cwd=repo_dir)
            await process.run("git", "pull", "-q", cwd=repo_dir)

    shell_dir = base_dir / "tinted-shell"
    base16_dir = data_dir / "base16-shell"
    if os.path.realpath(base16_dir) != str(shell_dir):
        fs.delete(base16_dir)
        base16_dir.symlink_to(shell_dir)
