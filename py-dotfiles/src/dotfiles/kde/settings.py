import dataclasses
import os
import pathlib

from dotfiles import fs, process, xdg

from . import kconfig


@dataclasses.dataclass
class GlobalShortcut:
    name: str
    exec: str
    shortcut: str

    @property
    def desktop_id(self):
        command = self.exec.split()[0]
        basename = pathlib.Path(command).name
        return basename


HOME = pathlib.Path("~").expanduser()
CONFIG = HOME / ".config"
LOCAL_SHARE = HOME / ".local" / "share"


class Rsync:
    @staticmethod
    async def copy_into_replace_contents(source, target):
        target.mkdir(exist_ok=True, parents=True)
        await process.run("rsync", "-avq", "--delete", f"{source}/", target)

    @staticmethod
    async def copy_replace(source, target):
        target.parent.mkdir(exist_ok=True, parents=True)
        await process.run("rsync", "-avq", source, target)


def links(hostname, dotfiles):
    result = {
        LOCAL_SHARE / "icons": dotfiles / "kde" / "icons",
        LOCAL_SHARE / "applications": dotfiles / "kde" / "applications",
        LOCAL_SHARE / "kwin": dotfiles / "kde" / "kwin",
    }
    match hostname:
        case "mars" | "phobos":
            result[CONFIG / "autostart"] = (
                dotfiles / "kde" / "autostart" / hostname
            )
    return result


def write_desktop_file(name, exec, desktop_id):
    desktop_file = (
        LOCAL_SHARE
        / "applications"
        / f"net.local.dotfiles.{desktop_id}.desktop"
    )
    desktop_content = f"""[Desktop Entry]
Exec={exec}
Name={name}
NoDisplay=true
StartupNotify=false
Type=Application
X-KDE-GlobalAccel-CommandShortcut=true
"""
    desktop_file.parent.mkdir(parents=True, exist_ok=True)
    desktop_file.write_text(desktop_content)


def global_shortcuts(hostname, dotfiles):
    match hostname:
        case "lounge-htpc":
            return [
                GlobalShortcut(
                    name="Lounge HTPC Brightness Max",
                    exec="lounge-htpc-brightness-max.sh",
                    shortcut="Back",
                ),
                GlobalShortcut(
                    name="Lounge HTPC Brightness Min",
                    exec="lounge-htpc-brightness-min.sh",
                    shortcut="Home Page",
                ),
                GlobalShortcut(
                    name="Lounge HTPC Power Toggle",
                    exec="lounge-htpc-power-toggle.sh",
                    shortcut="Menu",
                ),
                GlobalShortcut(
                    name="Lounge HTPC Volume Down",
                    exec="lounge-htpc-volume-down.sh",
                    shortcut="Volume Down",
                ),
                GlobalShortcut(
                    name="Lounge HTPC Volume Mute Toggle",
                    exec="lounge-htpc-volume-mute-toggle.sh",
                    shortcut="Volume Mute",
                ),
                GlobalShortcut(
                    name="Lounge HTPC Volume Up",
                    exec="lounge-htpc-volume-up.sh",
                    shortcut="Volume Up",
                ),
            ]
        case "mars" | "phobos":
            return [
                GlobalShortcut(
                    name="Center and scale the focused window",
                    exec=str(dotfiles / "kde" / "kde-center-scaled"),
                    shortcut="Meta+Shift+C",
                ),
                GlobalShortcut(
                    name="Toggle tmux-scratchpad",
                    exec=str(dotfiles / "kde" / "kde-toggle-tmux-scratchpad"),
                    shortcut="Meta+Return",
                ),
                GlobalShortcut(
                    name="Toggle Obsidian",
                    exec=str(dotfiles / "kde" / "kde-toggle-obsidian"),
                    shortcut="Meta+n",
                ),
            ]
        case _:
            return []


def unique_desktop_ids(shortcuts):
    counts = {}
    for shortcut in shortcuts:
        counts[shortcut.desktop_id] = counts.get(shortcut.desktop_id, 0) + 1

    usage = {}
    unique_ids = []
    for shortcut in shortcuts:
        base_id = shortcut.desktop_id
        if counts[base_id] > 1:
            counter = usage.get(base_id, 0) + 1
            usage[base_id] = counter
            unique_ids.append(f"{base_id}-{counter}")
        else:
            unique_ids.append(base_id)
    return unique_ids


async def warn_if_logout_needed():
    runtime_dir = pathlib.Path(
        os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    )
    pid_file = runtime_dir / "kde-shortcuts-kwin-pid"

    try:
        result = await process.run(
            "pgrep", "-x", "kwin_wayland", check=False, stdout=process.PIPE
        )
        current_pid = result.stdout.decode().strip()
    except Exception:
        current_pid = ""

    try:
        stored_pid = pid_file.read_text().strip()
    except FileNotFoundError:
        stored_pid = ""

    if current_pid and current_pid != stored_pid:
        pid_file.write_text(current_pid)
        if not stored_pid:
            print("WARNING: Logout required to load updated shortcuts.")
    elif stored_pid and current_pid == stored_pid:
        print("WARNING: Logout required to load updated shortcuts.")


async def configure_kde(hostname, dotfiles):
    settings = {
        "kwinrc": {
            "org.kde.kdecoration2": {
                "ButtonsOnLeft": "FS",
                "ShowToolTips": "false",
            },
            "Plugins": {
                "dialogparentEnabled": "false",
            },
        },
        "kdesurc": {
            "super-user-command": {
                "super-user-command": "sudo",
            }
        },
        "kuriikwsfilterrc": {
            "General": {
                "DefaultWebShortcut": "google",
                "EnableWebShortcuts": "true",
                "KeywordDelimiter": ":",
                "PreferredWebShortcuts": "google,youtube,wikit,yahoo,wikipedia",
                "UsePreferredWebShortcutsOnly": "false",
            }
        },
        "dolphinrc": {
            "KDE": {
                "AnimationDurationFactor": "0",
            },
            "MainWindow": {
                "MenuBar": "Disabled",
            },
            "General": {
                "OpenNewTabAfterLastTab": "true",
                "ShowFullPath": "true",
            },
        },
        "kglobalshortcutsrc": {
            "kwin": {
                "Window Above Other Windows": "Meta+A,,Keep Window Above Others",
                "Window Fullscreen": "Meta+Shift+F,,Make Window Fullscreen",
                "Window Maximize": "Meta+PgUp\tMeta+F,Meta+PgUp,Maximize Window",
                "Window Move Center": "Meta+C,,Move Window to the Center",
            },
            "plasmashell": {
                "activate application launcher": "Alt+F1,Meta\tAlt+F1,Activate Application Launcher",
            },
            ("services", "org.kde.krunner.desktop"): {
                "_launch": "Search\tAlt+F2\tMeta+Space",
            },
        },
    }

    for file, file_groups in settings.items():
        for group, keys in file_groups.items():
            groups = list(group) if isinstance(group, tuple) else group
            for key, value in keys.items():
                await kconfig.kwriteconfig6(
                    file=file,
                    groups=groups,
                    key=key,
                    value=value,
                    notify=True,
                )

    shortcuts = global_shortcuts(hostname, dotfiles)
    unique_ids = unique_desktop_ids(shortcuts)

    for shortcut, unique_id in zip(shortcuts, unique_ids):
        write_desktop_file(
            name=shortcut.name,
            exec=shortcut.exec,
            desktop_id=unique_id,
        )

    for shortcut, unique_id in zip(shortcuts, unique_ids):
        await kconfig.kwriteconfig6(
            file="kglobalshortcutsrc",
            groups=["services", f"net.local.dotfiles.{unique_id}.desktop"],
            key="_launch",
            value=shortcut.shortcut,
            notify=True,
        )

    await warn_if_logout_needed()

    applications_dir = LOCAL_SHARE / "applications"
    expected_files = {
        applications_dir / f"net.local.dotfiles.{unique_id}.desktop"
        for unique_id in unique_ids
    }
    if applications_dir.exists():
        for desktop_file in applications_dir.glob(
            "net.local.dotfiles.*.desktop"
        ):
            if desktop_file not in expected_files:
                desktop_file.unlink()


async def main():
    hostname = os.environ["HOST_DOTFILES"]
    dotfiles = fs.dotfiles()

    for path, target in links(hostname, dotfiles).items():
        fs.link(path, target)

    if hostname:
        source = dotfiles / "kde" / "applications_host" / hostname
        target = LOCAL_SHARE / "applications" / "dotfiles-localhost"
        if source.exists():
            await Rsync.copy_into_replace_contents(source, target)
        else:
            fs.delete(target)

    if hostname in ("mars", "phobos"):
        await xdg.update_desktop_database()

    await configure_kde(hostname, dotfiles)
