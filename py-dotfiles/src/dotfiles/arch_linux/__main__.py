import argparse
import asyncio
import grp
import os
import pathlib
import shutil
import sys

from dotfiles import (
    arch_linux,
    errors,
    flatpak,
    fs,
    process,
    systemd,
    users,
    uv,
)

SRC = pathlib.Path(__file__).resolve().parents[2]
MODULE = "dotfiles.arch_linux"

HOSTNAME = os.environ["HOST_DOTFILES"]

EXPECTED_PACKAGES = {
    "logrotate",
}

if HOSTNAME in ("sol", "mars", "phobos"):
    EXPECTED_PACKAGES.update(
        {
            "7zip",
            "advancecomp",
            "aria2",
            "aweber-cli",
            "base",
            "base-devel",
            "bat",
            "bchunk",
            "bind",  # dig
            "binmerge",
            "busybox",
            "cabextract",
            "cdemu-client",
            "clang",  # for clang-format
            "claude-code",
            "crun",
            "cuetools",
            "curlie",
            "dash",
            "devtools",
            "dolphin-emu-tool",
            "dosfstools",
            "e2fsprogs",
            "efibootmgr",
            "efivar",
            "epub-tools-bin",
            "exfatprogs",
            "fd",
            "ffmpeg",
            "fzf",
            "gifsicle",
            "git",
            "git-lfs",
            "github-cli",
            "guestfs-tools",
            "hdparm",
            "htop",
            "hugo",
            "hyperfine",
            "iftop",
            "imagemagick",
            "inetutils",  # hostname command
            "innoextract",
            "iperf3",
            "iw",
            "jpegoptim",
            "jq",
            "just",
            "less",
            "libva-utils",  # vainfo command
            "libvips",
            "mac",
            "man-db",
            "mediainfo",
            "moreutils",
            "mp3val",
            "mprime-bin",
            "mpv",
            "ms-sys",
            "neovim",
            "nfs-utils",
            "nmap",
            "nsz",
            "ntfs-3g",
            "openbsd-netcat",
            "openssh",
            "opus-tools",
            "oxipng",
            "pacman-contrib",
            "pandoc-cli",
            "pbzip2",
            "perl-image-exiftool",
            "pi-coding-agent",
            "pigz",
            "pixz",
            "pkgfile",
            "prek",
            "prettier",
            "pwgen",
            "pyalpm",
            "python",
            "rclone",
            "reflector",
            "ripgrep",
            "rsync",
            "ruff",
            "rustup",
            "shellcheck",
            "shntool",
            "speedtest-go",
            "sshfs",
            "sshuttle",
            "stylua",
            "svgo",
            "syncthing",
            "tcpdump",
            "time",
            "tmux",
            "tokei",
            "traceroute",
            "transmission-cli",
            "tree-sitter-cli",  # for neovim plugins
            "ty",
            "typescript-language-server",
            "unace",
            "unrar",
            "unshield",
            "unzip",
            "usbutils",
            "uv",
            "vim",
            "vorbis-tools",
            "which",
            "wl-clipboard",
            "xsel",
            "yazi",
            "yt-dlp",
            "zip",
            "zsh",
        }
    )

if HOSTNAME == "sol":
    EXPECTED_PACKAGES.add("iptables-nft")
else:
    EXPECTED_PACKAGES.add("iptables")

if HOSTNAME in ("mars", "phobos", "lounge-htpc"):
    EXPECTED_PACKAGES.update(
        {
            "firefox",
            "gamescope",
            "gwenview",
            "jellium-desktop-git",
            "kwalletmanager",
            "noto-fonts",
            "steam",
            "ttf-hack",
        }
    )

if HOSTNAME in ("phobos"):
    EXPECTED_PACKAGES.update(
        {
            "fastflowlm",
            "fprintd",
            "lemonade-server",
        }
    )

if HOSTNAME in ("mars", "phobos"):
    EXPECTED_PACKAGES.update(
        {
            "86box",
            "discimagecreator",
            "amd-ucode",
            "android-tools",
            "ark",
            "audacity",
            "avidemux-qt",
            "base16-shell-preview",
            "chromium",
            "discover",
            "docker",
            "docker-compose",
            "dolphin",
            "dosbox-staging",
            "dvd+rw-tools",
            "evtest",
            "flatpak-builder",
            "flatpak-kcm",
            "ghidra",
            "ghostty",
            "gifski",
            "gimp",
            "google-chrome",
            "gparted",
            "inkscape",
            "kcolorchooser",
            "kdeconnect",
            "kid3",
            "krdc",
            "krfb",
            "kubectl",
            "kwinctrl",
            "litra",
            "lsdvd",
            "makemkv",
            "meson",
            "mkvalidator",
            "mkvtoolnix-gui",
            "mpv-mpris",
            "nvme-cli",
            "obs-studio",
            "okular",
            "ollama-vulkan",
            "plasma-keyboard",
            "plasma-login-manager",
            "plasma6-runners-emojirunner",
            "plasma6-runners-markdown-bookmarks",
            "podman",
            "powertop",
            "print-manager",
            "radeontop",
            "realtime-privileges",
            "rawtherapee",
            "rife-ncnn-vulkan-bin",
            "rocm-hip-sdk",
            "rocm-opencl-runtime",
            "spectacle",
            "thunderbird",
            "typst",
            "udiskie",
            "virt-manager",
            "vlc",
            "vulkan-radeon",  # amdgpu
            "vulkan-virtio",
            "wine",
            "wireshark-qt",
            "xboxdrv",
            "yay",
        }
    )

EXPECTED_FLATPAKS = {
    "flathub": set(),
}

if HOSTNAME in ("mars", "phobos"):
    EXPECTED_FLATPAKS["flathub"].update(
        {
            "com.bitwarden.desktop",
            "com.bitwig.BitwigStudio",
            "com.valvesoftware.Steam.CompatibilityTool.Proton-GE",
            "im.riot.Riot",
            "md.obsidian.Obsidian",
            "org.equeim.Tremotesf",
            "org.fooyin.fooyin",
            "org.prismlauncher.PrismLauncher",
            "org.signal.Signal",
        }
    )

EXPECTED_FLATPAK_SOCKETS = {
    "md.obsidian.Obsidian": {"wayland"},
}

VHBA_MODULE_PACKAGE = "vhba-module"
if HOSTNAME in ("sol"):
    VHBA_MODULE_PACKAGE = "vhba-module-dkms"

EXPECTED_PACKAGE_DEPENDENCIES = {
    "86box": {
        "86box-roms",
    },
    "android-tools": {
        "android-udev",
    },
    "ark": {
        "7zip",
        "arj",
        "lrzip",
        "lzop",
        "unarchiver",
        "unrar",
    },
    "asusctl": {
        "supergfxctl",
    },
    "breeze": {
        "breeze-gtk",
    },
    "cdemu-daemon": {
        "pulse-native-provider",
        VHBA_MODULE_PACKAGE,
    },
    "cmake": {
        "ninja",
    },
    "devtools": {
        "bat",
        "btrfs-progs",
        "nvchecker",
    },
    "digikam": {
        "hugin",
        "qt6-imageformats",
    },
    "dolphin": {
        "ffmpegthumbs",
        "kde-cli-tools",
        "kdegraphics-thumbnailers",
        "kio-admin",
        "konsole",
        "purpose",
    },
    "foot": {
        "foot-terminfo",
    },
    "gimp": {
        "alsa-lib",
        "cfitsio",
        "ghostscript",
        "gjs",
        "gutenprint",
        "gvfs",
    },
    "gwenview": {
        "kimageformats",
        "qt6-imageformats",
    },
    "gparted": {
        "btrfs-progs",
        "dosfstools",
        "exfatprogs",
        "f2fs-tools",
        "gpart",
        "mtools",
        "ntfs-3g",
        "polkit",
        "udftools",
        "xfsprogs",
        "xorg-xhost",
    },
    "libvips": {
        "imagemagick",
        "libheif",
        "libjxl",
        "openslide",
        "poppler-glib",
        "python",
    },
    "neovim": {
        "wl-clipboard",
    },
    "networkmanager": {
        "bluez",
        "dhcpcd",
        "dnsmasq",
        "iptables",
        "iwd",
        "nftables",
        "systemd-resolvconf",
    },
    "libvirt": {
        "dmidecode",
        "dnsmasq",
        "gettext",
        "iptables",
        "lvm2",
        "qemu-desktop",
        "swtpm",
    },
    "kcrash": {
        "drkonqi",
    },
    "krita": {
        "kimageformats",
        "krita-plugin-gmic",
        "kseexpr",
        "libheif",
        "libjxl",
        "libmypaint",
        "poppler-qt6",
        "python-pyqt6",
    },
    "lutris": {
        "fluidsynth",
        "gamemode",
        "gvfs",
        "innoextract",
        "lib32-gamemode",
        "lib32-vkd3d",
        "lib32-vulkan-icd-loader",
        "python-protobuf",
        "vkd3d",
        "vulkan-icd-loader",
        "vulkan-tools",
        "wine",
        "xorg-xgamma",
    },
    "noto-fonts": {
        "noto-fonts-cjk",
        "noto-fonts-emoji",
        "noto-fonts-extra",
    },
    "okular": {
        "ebook-tools",
        "kdegraphics-mobipocket",
        "unrar",
    },
    "perl-image-exiftool": {
        "perl-archive-zip",
        "perl-io-compress-brotli",
    },
    "pipewire": {
        "pipewire-alsa",
        "pipewire-jack",
        "pipewire-pulse",
    },
    "plasma-desktop": {
        "bluedevil",
        "kscreen",
        "packagekit-qt6",
        "plasma-nm",
        "plasma-pa",
    },
    "plasma-workspace": {
        "xdg-desktop-portal-gtk",
    },
    "print-manager": {
        "system-config-printer",
    },
    "python": {
        "python-setuptools",
        "python-pip",
        "sqlite",
        "xz",
        "tk",
    },
    "python-aiohttp": {
        "python-aiodns",
    },
    "udiskie": {
        "libappindicator",
    },
    "vulkan-radeon": {
        "lib32-vulkan-radeon",
    },
    "wine": {
        "alsa-plugins",
        "cups",
        "dosbox",
        "gnutls",
        "gst-plugins-bad",
        "gst-plugins-base",
        "gst-plugins-base-libs",
        "gst-plugins-good",
        "gst-plugins-ugly",
        "libgphoto2",
        "libpulse",
        "libxcomposite",
        "libxinerama",
        "opencl-icd-loader",
        "pcsclite",
        "samba",
        "sane",
        "sdl2-compat",
        "unixodbc",
        "v4l-utils",
        "wine-gecko",
        "wine-mono",
    },
    "xdg-utils": {
        # needed to correctly identify .cbz as application/vnd.comicbook+zip
        "perl-file-mimeinfo",
    },
    "yazi": {
        "7zip",
        "chafa",
        "fd",
        "ffmpeg",
        "fzf",
        "imagemagick",
        "jq",
        "poppler",
        "ripgrep",
        "wl-clipboard",
        "zoxide",
    },
    "yt-dlp": {
        "aria2",
        "atomicparsley",
        "ffmpeg",
        "python-brotli",
        "python-brotlicffi",
        "python-pycryptodome",
        "python-pycryptodomex",
        "python-pyxattr",
        "python-secretstorage",
        "python-websockets",
        "python-xattr",
        "rtmpdump",
        "yt-dlp-ejs",
    },
}

EXPECTED_GROUPS = {}

EXPECTED_SERVICES = {
    "fstrim.timer",
    "logrotate.timer",
    "systemd-timesyncd.service",
}

if HOSTNAME in ("mars", "phobos"):
    EXPECTED_SERVICES.update(
        {
            "avahi-daemon.service",
            "cups.service",
            "plasmalogin.service",
        }
    )

EFI_SHELL_HOSTS = ("mars", "phobos", "lounge-htpc", "sol")
if HOSTNAME in EFI_SHELL_HOSTS:
    EXPECTED_PACKAGES.add("edk2-shell")
    EXPECTED_SERVICES.add("systemd-boot-update.service")

if HOSTNAME in ("lounge-htpc"):
    EXPECTED_GROUPS.setdefault("lounge-htpc", set())
    EXPECTED_GROUPS["lounge-htpc"].update(
        {
            "audio",
            "games",
            "nopasswdlogin",
            #            "realtime",
            "video",
            "wheel",
        }
    )

if HOSTNAME in ("mars", "phobos"):
    EXPECTED_PACKAGE_DEPENDENCIES.setdefault("podman", set())
    EXPECTED_PACKAGE_DEPENDENCIES["podman"].update(
        {
            "apparmor",
            "btrfs-progs",
            "fuse-overlayfs",
            "podman-compose",
            "slirp4netns",
        }
    )

    EXPECTED_PACKAGE_DEPENDENCIES.setdefault("docker", set())
    EXPECTED_PACKAGE_DEPENDENCIES["docker"].update(
        {
            "btrfs-progs",
            "docker-buildx",
            "pigz",
        }
    )

    EXPECTED_GROUPS.setdefault("ar", set())
    EXPECTED_GROUPS["ar"].update(
        {
            "audio",
            "cdemu",
            "docker",
            "games",  # for proton to automatically set niceness
            "realtime",
            "libvirt",
            "libvirt-qemu",
            "storage",
            "video",
            "wheel",
        }
    )

if HOSTNAME in ("lounge-htpc", "mars"):
    EXPECTED_PACKAGES.update(
        {
            "linux",
            "linux-headers",
        }
    )

if HOSTNAME in ("lounge-htpc", "mars", "phobos"):
    EXPECTED_PACKAGES.update(
        {
            "plymouth",
            "plymouth-kcm",
        }
    )

if HOSTNAME == "mars":
    EXPECTED_PACKAGES.update(
        {
            "digikam",
        }
    )

if HOSTNAME in ("lounge-htpc", "phobos", "sol"):
    EXPECTED_PACKAGES.update(
        {
            "linux-lts",
            "linux-lts-headers",
        }
    )
    EXPECTED_SERVICES.update(
        {
            "smb.service",
        }
    )


async def install_efi_shell():
    source = pathlib.Path("/usr/share/edk2-shell/x64/Shell_Full.efi")
    target = pathlib.Path("/boot/shellx64.efi")

    if not target.exists() or fs.sha256(source) != fs.sha256(target):
        print("Installing", target)
        shutil.copyfile(source, target)


async def ensure_python_freethreaded():
    python_path = await uv.UV.find_python("3.14t")

    if python_path is None:
        print("Installing Python 3.14 freethreaded via uv")
        await uv.UV.install_python("3.14t")
        python_path = await uv.UV.find_python("3.14t")

    local_bin = pathlib.Path.home() / ".local" / "bin"
    local_bin.mkdir(parents=True, exist_ok=True)

    for name in ("python3", "python"):
        link_path = local_bin / name
        if link_path.is_symlink() or link_path.exists():
            if link_path.resolve() == python_path:
                continue
            link_path.unlink()

        print(f"Linking {link_path} to {python_path}")
        link_path.symlink_to(python_path)


async def ensure_using_systemd_resolved():
    unit = "systemd-resolved"
    if await systemd.Systemctl.is_enabled(unit):
        await systemd.Systemctl.enable(unit)

    source = pathlib.Path("/run/systemd/resolve/stub-resolv.conf")
    target = pathlib.Path("/etc/resolv.conf")
    if target.resolve() != source:
        print(f"Linking {target} to {source}")
        try:
            target.unlink()
        except FileNotFoundError:
            pass
        target.symlink_to(source)


async def ensure_users_in_expected_groups():
    for user, expected_groups in EXPECTED_GROUPS.items():
        current_groups = {
            g.gr_name for g in grp.getgrall() if user in g.gr_mem
        }
        for group in expected_groups - current_groups:
            await users.UserGroup.add_to_group(user, group)


async def ensure_flatpak_permissions():
    # Note: using :ro will always result in a portal path like /run/user/1000/doc/74ae3507/Library
    flatpak_permissions = {}

    match HOSTNAME:
        case "mars":
            # portal paths are not consistent,
            # likely due to /storage being an NFS mount.
            # eg. it could initially be /run/user/1000/doc/74ae3507/Library, but change to /run/user/1000/doc/efd6054f after a reboot
            flatpak_permissions["org.fooyin.fooyin"] = [
                "/storage/Audio/Library",
            ]
        case "phobos":
            flatpak_permissions["org.fooyin.fooyin"] = [
                "/home/ar/Audio/Library/:ro",
            ]

    installed_flatpaks = await flatpak.Flatpak.list_installed()

    for app, paths in flatpak_permissions.items():
        if app not in installed_flatpaks:
            continue

        current_perms = await flatpak.Flatpak.get_permissions(app)

        for path in paths:
            # Normalize path for comparison - remove slash before :ro/:rw suffix
            normalized_path = path.replace("/:", ":")
            if not any(p == normalized_path for p in current_perms):
                print(f"Granting {app} access to {path}")
                await flatpak.Flatpak.override_filesystem(app, path)

    for app, sockets in EXPECTED_FLATPAK_SOCKETS.items():
        if app not in installed_flatpaks:
            continue

        current_sockets = await flatpak.Flatpak.get_sockets(app)
        for socket in sockets - current_sockets:
            print(f"Granting {app} socket {socket}")
            await flatpak.Flatpak.override_socket(app, socket)


async def dump_installed_packages():
    dotfiles_private = os.environ.get("DOTFILES_PRIVATE")
    if not dotfiles_private:
        return

    output_file = (
        pathlib.Path(dotfiles_private)
        / "arch-linux"
        / f"packages_{HOSTNAME}.txt"
    )
    packages = sorted(arch_linux.pacman.local_packages(), key=lambda p: p.name)

    lines = []
    for pkg in packages:
        reason = (
            "explicit" if arch_linux.pacman.is_explicit(pkg) else "dependency"
        )
        lines.append(f"{pkg.name} {reason}")

    output_file.write_text("\n".join(lines) + "\n")


async def ensure_flatpaks():
    if not shutil.which("flatpak"):
        return
    installed_flatpaks = await flatpak.Flatpak.list_installed()

    for remote, expected_apps in EXPECTED_FLATPAKS.items():
        missing = expected_apps - installed_flatpaks

        if missing:
            print(f"Installing missing flatpaks from {remote} ...")
            for app in missing:
                print(f"  Installing {app}")
                await flatpak.Flatpak.install(remote, app)

    await ensure_flatpak_permissions()


async def ensure_packages():
    expected_packages = set(EXPECTED_PACKAGES)
    installed_packages = {
        package.name: package for package in arch_linux.pacman.local_packages()
    }

    missing = set()
    wrong_reason = set()
    for name in expected_packages:
        if name not in installed_packages:
            missing.add(name)
        elif not arch_linux.pacman.is_explicit(installed_packages[name]):
            wrong_reason.add(name)

    if missing:
        print("Installing missing packages ...")
        await arch_linux.pacman.Pacman.install(missing)

    if wrong_reason:
        print("Marking packages as explicitly installed ...")
        await arch_linux.pacman.Pacman.set_reason(wrong_reason, explicit=True)


async def ensure_package_dependencies():
    provided_packages = set()
    installed_packages = set()
    for package in arch_linux.pacman.local_packages():
        installed_packages.add(package.name)
        provided_packages.add(package.name)
        provided_packages.update(package.provides)

    missing = set()
    for package, expected_deps in EXPECTED_PACKAGE_DEPENDENCIES.items():
        if package not in installed_packages:
            continue
        for dep in expected_deps:
            if dep not in provided_packages:
                missing.add(dep)

    if missing:
        print("Installing missing dependencies ...")
        await arch_linux.pacman.Pacman.install(missing, asdeps=True)


async def run_mode(mode):
    args = []
    if mode == "root":
        args.extend(["sudo", "--preserve-env=HOST_DOTFILES"])
    args.extend([sys.executable, "-m", MODULE, mode])
    await process.run(*args, cwd=SRC)


async def main():
    modes = ["user", "root"]
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=modes, nargs="?")
    args = parser.parse_args()

    # TODO: always run as root
    match args.mode:
        case "user":
            await ensure_packages()
            await ensure_package_dependencies()
            await ensure_flatpaks()
            await dump_installed_packages()

            await ensure_users_in_expected_groups()

            # if HOSTNAME in ("mars", "phobos", "sol"):
            if HOSTNAME in ():
                await ensure_python_freethreaded()

            for service in EXPECTED_SERVICES:
                await systemd.Systemctl.enable(service, now=True)
        case "root":
            if HOSTNAME in ("mars", "phobos"):
                await ensure_using_systemd_resolved()
            if HOSTNAME in EFI_SHELL_HOSTS:
                await install_efi_shell()
        case _:
            for mode in modes:
                await run_mode(mode)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (errors.ProcessError, errors.UserError) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
