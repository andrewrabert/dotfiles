import contextlib
import importlib
import io
import os
import pathlib
import socket
import sys

from dotfiles import errors, process

YELLOW = "\033[1;33m"
RESET_COLOR = "\033[0m"
BREW_GNUBIN = pathlib.Path("/opt/homebrew/opt/coreutils/libexec/gnubin")
DOTFILES_SCRIPT = "00-dotfiles"
PIKVM = "pikvm"
PIKVM_SCRIPTS = ["00-dotfiles", "10-pikvm", "60-tmux", "60-zsh"]
ZSH_OVERRIDE = (
    "if [ -f ~/.zshenv.local ]; then . ~/.zshenv.local; fi"
    ' && echo "$HOST_DOTFILES"'
)
SCRIPTS = {
    "00-dotfiles": "dotfiles.full_update.dotfiles:main",
    "10-arch-linux": "dotfiles.arch_linux:main",
    "10-fedora-kinoite": "dotfiles.full_update.fedora_kinoite:main",
    "10-macos": "dotfiles.macos:main",
    "10-pikvm": "dotfiles.full_update.pikvm:main",
    "10-termux": "dotfiles.full_update.termux:main",
    "20-flatpak": "dotfiles.full_update.flatpak:main",
    "30-nvm": "dotfiles.full_update.nvm:main",
    "30-rust": "dotfiles.full_update.rust:main",
    "35-uv": "dotfiles.full_update.uv:main",
    "40-jpegli": "dotfiles.full_update.jpegli:main",
    "50-podman": "dotfiles.full_update.podman:main",
    "60-base16-shell": "dotfiles.full_update.base16_shell:main",
    "60-bertbox": "dotfiles.commands.bertbox:main",
    "60-bxwrp": "dotfiles.commands.bxwrp:main",
    "60-dash": "dotfiles.full_update.dash:main",
    "60-discord": "dotfiles.commands.discord:main",
    "60-dosbox": "dotfiles.full_update.dosbox:main",
    "60-fontconfig": "dotfiles.full_update.fontconfig:main",
    "60-foot": "dotfiles.full_update.foot:main",
    "60-fwupd": "dotfiles.full_update.fwupd:main",
    "60-ghostty": "dotfiles.full_update.ghostty:main",
    "60-git-sync": "dotfiles.full_update.git_sync:main",
    "60-kde": "dotfiles.kde.settings:main",
    "60-krita": "dotfiles.commands.krita:main",
    "60-mpv": "dotfiles.full_update.mpv:main",
    "60-neovim": "dotfiles.full_update.neovim:main",
    "60-networkmanager": "dotfiles.full_update.networkmanager:main",
    "60-noted": "dotfiles.commands.noted:main",
    "60-pi": "dotfiles.full_update.pi:main",
    "60-pipewire": "dotfiles.full_update.pipewire:main",
    "60-psql": "dotfiles.full_update.psql:main",
    "60-remove-broken-symlinks": "dotfiles.full_update.remove_broken_symlinks:main",
    "60-tmux": "dotfiles.full_update.tmux:main",
    "60-update-mime-database": "dotfiles.full_update.update_mime_database:main",
    "60-yazi": "dotfiles.full_update.yazi:main",
    "60-zed": "dotfiles.full_update.zed:main",
    "60-zoekt-simple": "dotfiles.commands.zoekt_simple:main",
    "60-zsh": "dotfiles.full_update.zsh:main",
    "65-kde-color-schemes": "dotfiles.kde.color_schemes:main",
    "70-ruff-config": "dotfiles.full_update.ruff_config:main",
    "99-arch-linux": "dotfiles.arch_linux:main_99",
    "99-host-bedroom-tv": "dotfiles.full_update.host_bedroom_tv:main",
    "99-host-mars": "dotfiles.commands.host_mars:main",
    "99-host-sol": "dotfiles.full_update.host_sol:main",
    "99-host-termux": "dotfiles.full_update.host_termux:main",
    "99-macos": "dotfiles.macos.packages:main",
    "99-syncthing": "dotfiles.commands.syncthing:main",
}


def announce(message):
    print(f"{YELLOW}{message}{RESET_COLOR}", flush=True)


async def capture_if_installed(*command, env=None):
    try:
        result = await process.run(*command, env=env, stdout=process.PIPE)
    except FileNotFoundError:
        return None
    return result.stdout.decode().strip()


async def resolve_host():
    name = socket.gethostname()
    override = await capture_if_installed(
        "zsh", "-lic", ZSH_OVERRIDE, env={**os.environ, "HOST_DOTFILES": name}
    )
    if override is not None:
        name = override
    hostnamectl = await capture_if_installed("hostnamectl", "hostname")
    if hostnamectl is not None:
        name = hostnamectl
    if not name:
        raise errors.UserError("cannot determine hostname")
    return name


def script_dirs():
    return [
        pathlib.Path(os.environ[name]) / "full-update"
        for name in sorted(os.environ)
        if name.startswith("DOTFILES_")
    ]


def is_read_only_root():
    with open("/proc/mounts") as mounts:
        for line in mounts:
            fields = line.split()
            if (
                len(fields) > 3
                and fields[1] == "/"
                and "ro" in fields[3].split(",")
            ):
                return True
    return False


@contextlib.asynccontextmanager
async def writable_root():
    if not is_read_only_root():
        yield
        return
    await process.run("rw")
    try:
        yield
    finally:
        await process.run("ro")


def setup_environment(host):
    os.environ["HOST_DOTFILES"] = host
    if BREW_GNUBIN.is_dir():
        os.environ["PATH"] = os.pathsep.join(
            [str(BREW_GNUBIN), os.environ.get("PATH", "")]
        )


async def run_script(key, args=()):
    module, name = SCRIPTS[key].split(":")
    function = getattr(importlib.import_module(module), name)
    announce(f"Running {key} ...")
    await function(list(args))


async def run_external(script, args=()):
    announce(f"Running {script.name} ...")
    await process.run(script, *args, env=os.environ)


async def run_named(name, args=()):
    if name in SCRIPTS:
        await run_script(name, args)
    for directory in script_dirs():
        script = directory / name
        if script.is_file():
            await run_external(script, args)


async def run_all(directory, skip):
    if not directory.is_dir():
        return
    refresh = directory / DOTFILES_SCRIPT
    if refresh.is_file():
        if DOTFILES_SCRIPT in skip:
            announce(f"Skipping {DOTFILES_SCRIPT}")
        else:
            await run_external(refresh, ["--system"])
    names = sorted(
        path.name
        for path in directory.iterdir()
        if not path.name.startswith(".")
    )
    for name in names:
        if name == DOTFILES_SCRIPT:
            continue
        if name in skip:
            announce(f"Skipping {name}")
            continue
        script = directory / name
        if script.is_file():
            await run_external(script)


async def run_builtin(skip):
    if DOTFILES_SCRIPT in skip:
        announce(f"Skipping {DOTFILES_SCRIPT}")
    else:
        await run_script(DOTFILES_SCRIPT, ["--system"])
    for name in sorted(SCRIPTS):
        if name == DOTFILES_SCRIPT:
            continue
        if name in skip:
            announce(f"Skipping {name}")
            continue
        await run_script(name)


async def main(skip, script, script_args):
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(line_buffering=True)
    host = await resolve_host()
    setup_environment(host)
    root = writable_root() if host == PIKVM else contextlib.nullcontext()
    async with root:
        if script is not None:
            script = pathlib.Path(script).name
            await run_named(script, script_args)
        elif host == PIKVM:
            for name in PIKVM_SCRIPTS:
                await run_named(name)
        else:
            await run_builtin(skip)
            for directory in script_dirs():
                await run_all(directory, skip)
