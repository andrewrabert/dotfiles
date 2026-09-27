import os
import pathlib

from dotfiles import fs, host

HOST_DIRS = {
    "aweber": ["scripts/mcp", ".local/zoekt-simple/bin"],
    "mars": ["scripts/media", ".local/zoekt-simple/bin"],
    "sol": ["scripts/media", ".local/zoekt-simple/bin"],
    "phobos": [
        "scripts/mcp",
        "scripts/media",
        ".local/zoekt-simple/bin",
    ],
}


def extra_roots():
    return [
        pathlib.Path(os.environ[name])
        for name in sorted(os.environ)
        if name.startswith("DOTFILES_")
    ]


def is_executable_file(path):
    return path.is_file() and os.access(path, os.X_OK)


def installed_commands(dest):
    commands = set()
    for entry in os.environ["PATH"].split(os.pathsep):
        directory = pathlib.Path(entry)
        if not directory.is_dir() or directory == dest:
            continue
        commands.update(
            path.name
            for path in directory.iterdir()
            if is_executable_file(path)
        )
    return commands


def collect_sources(primary, extras, hostname, dest):
    """Link sources in precedence order: a later source overrides an earlier one."""
    sources = [primary / "scripts/hosts" / hostname]
    sources.extend(root / "scripts/hosts" / hostname for root in extras)

    installed = installed_commands(dest)
    sources.extend(
        path
        for path in (primary / "scripts/commands").iterdir()
        if path.name in installed
    )

    sources.append(primary / "scripts/terminal")
    sources.append(primary / ".local/noted/bin")
    sources.append(primary / ".local/bertbox/bin")
    sources.append(primary / ".local/bertbox/install")
    sources.append(primary / ".local/bxwrp/bin")
    sources.extend(root / "scripts/terminal" for root in extras)
    sources.extend(primary / d for d in HOST_DIRS.get(hostname, []))
    return sources


def link_target(path):
    if path.is_symlink():
        path = path.parent / path.readlink()
    return path.absolute()


def collect_links(sources):
    links = {}
    for source in sources:
        if not source.exists():
            continue
        paths = [source] if source.is_file() else source.iterdir()
        for path in paths:
            links[path.name] = link_target(path)
    return links


def install(links, dest):
    for stale in dest.iterdir():
        if stale.name not in links:
            stale.unlink()
    for name, target in links.items():
        fs.link(dest / name, target)


def main():
    primary = fs.dotfiles()
    dest = primary / ".local/bin"
    dest.mkdir(parents=True, exist_ok=True)

    sources = collect_sources(primary, extra_roots(), host.name(), dest)
    install(collect_links(sources), dest)
    fs.link(primary / ".bin", dest)
