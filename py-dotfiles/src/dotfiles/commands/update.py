import contextlib
import os
import pathlib
import socket

from dotfiles import errors, fs, process

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
    extras = [
        pathlib.Path(os.environ[name])
        for name in sorted(os.environ)
        if name.startswith("DOTFILES_")
    ]
    return [root / "full-update" for root in [fs.dotfiles(), *extras]]


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


class Runner:
    def __init__(self, host):
        self.env = {**os.environ, "HOST_DOTFILES": host}
        if BREW_GNUBIN.is_dir():
            self.env["PATH"] = os.pathsep.join(
                [str(BREW_GNUBIN), os.environ.get("PATH", "")]
            )

    async def run(self, script, args=()):
        announce(f"Running {script.name} ...")
        await process.run(script, *args, env=self.env)

    async def run_named(self, name, args=()):
        for directory in script_dirs():
            script = directory / name
            if script.is_file():
                await self.run(script, args)

    async def run_all(self, directory, skip):
        if not directory.is_dir():
            return
        refresh = directory / DOTFILES_SCRIPT
        if refresh.is_file():
            if DOTFILES_SCRIPT in skip:
                announce(f"Skipping {DOTFILES_SCRIPT}")
            else:
                await self.run(refresh, ["--system"])
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
                await self.run(script)


async def main(skip, script, script_args):
    host = await resolve_host()
    runner = Runner(host)
    root = writable_root() if host == PIKVM else contextlib.nullcontext()
    async with root:
        if script is not None:
            await runner.run_named(script, script_args)
        elif host == PIKVM:
            for name in PIKVM_SCRIPTS:
                await runner.run_named(name)
        else:
            for directory in script_dirs():
                await runner.run_all(directory, skip)
