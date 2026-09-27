"""full-update commands for dotfiles."""

import argparse
import asyncio
import sys

from dotfiles import errors
from dotfiles.commands import (
    bertbox,
    bxwrp,
    discord,
    host_mars,
    jellium_desktop,
    krita,
    link_bin,
    noted,
    syncthing,
    update,
    zoekt_simple,
)

PASSTHROUGH = {"bertbox", "bxwrp", "noted"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_passthrough(name, help):
        subparsers.add_parser(name, help=help, add_help=False)

    add_passthrough("bertbox", "Manage bertbox")
    add_passthrough("bxwrp", "Manage bxwrp")
    subparsers.add_parser("discord", help="disable discord host updates")
    subparsers.add_parser("host-mars", help="configure the mars host")
    jellium_parser = subparsers.add_parser(
        "jellium-desktop", help="install the Jellium Desktop nightly"
    )
    jellium_parser.add_argument(
        "platform", choices=sorted(jellium_desktop.PLATFORMS)
    )
    jellium_parser.add_argument(
        "--ssh", metavar="HOST", help="install on HOST over SSH"
    )

    subparsers.add_parser("kde", help="configure KDE Plasma")
    subparsers.add_parser(
        "kde-color-schemes", help="generate per-app titlebar colors"
    )
    subparsers.add_parser("krita", help="launch krita without splash")
    subparsers.add_parser(
        "link-bin", help="link dotfiles scripts into the dotfiles bin"
    )
    subparsers.add_parser("macos", help="install expected homebrew packages")
    add_passthrough("noted", "Manage noted")
    subparsers.add_parser("syncthing", help="write .stignore includes")

    update_parser = subparsers.add_parser(
        "update", help="run every full-update script"
    )
    update_parser.add_argument(
        "--skip",
        action="append",
        default=[],
        metavar="NAME",
        help="skip script by name (can be repeated)",
    )
    update_parser.add_argument(
        "script", nargs="?", help="run only this script"
    )
    update_parser.add_argument(
        "script_args",
        nargs=argparse.REMAINDER,
        metavar="ARG",
        help="arguments passed to SCRIPT",
    )

    subparsers.add_parser("zoekt-simple", help="Manage zoekt-simple")

    args, rest = parser.parse_known_args()
    if rest and args.command not in PASSTHROUGH:
        parser.error(f"unrecognized arguments: {' '.join(rest)}")
    try:
        match args.command:
            case "bertbox":
                asyncio.run(bertbox.main(rest))
            case "bxwrp":
                asyncio.run(bxwrp.main(rest))
            case "discord":
                asyncio.run(discord.main([]))
            case "host-mars":
                asyncio.run(host_mars.main([]))
            case "jellium-desktop":
                asyncio.run(jellium_desktop.main(args.platform, args.ssh))
            case "kde":
                from dotfiles.kde import settings

                asyncio.run(settings.main([]))
            case "kde-color-schemes":
                from dotfiles.kde import color_schemes

                asyncio.run(color_schemes.main([]))
            case "krita":
                asyncio.run(krita.main([]))
            case "link-bin":
                link_bin.main()
            case "macos":
                from dotfiles.macos import packages

                asyncio.run(packages.main([]))
            case "noted":
                asyncio.run(noted.main(rest))
            case "syncthing":
                asyncio.run(syncthing.main([]))
            case "update":
                asyncio.run(
                    update.main(args.skip, args.script, args.script_args)
                )
            case "zoekt-simple":
                asyncio.run(zoekt_simple.main([]))
    except (errors.ProcessError, errors.UserError) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
