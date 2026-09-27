import pathlib


def remove_broken_symlinks(directory):
    if not directory.is_dir():
        return
    for path in directory.iterdir():
        if path.is_symlink() and not path.exists():
            path.unlink(missing_ok=True)


async def main(args):
    remove_broken_symlinks(pathlib.Path.home() / ".local/bin")
