"""full-update commands for dotfiles."""

import argparse
import asyncio
import sys

from dotfiles import errors
from dotfiles.commands import (
    discord,
    host_mars,
    krita,
    link_bin,
    redump_verifier,
    syncthing,
    update,
)

PASSTHROUGH = {
    "redump-verifier",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_passthrough(name, help):
        subparsers.add_parser(name, help=help, add_help=False)

    subparsers.add_parser("discord", help="disable discord host updates")
    subparsers.add_parser("host-mars", help="configure the mars host")

    subparsers.add_parser("kde", help="configure KDE Plasma")
    subparsers.add_parser(
        "kde-color-schemes", help="generate per-app titlebar colors"
    )
    subparsers.add_parser("krita", help="launch krita without splash")
    subparsers.add_parser(
        "link-bin", help="link dotfiles scripts into the dotfiles bin"
    )
    subparsers.add_parser("macos", help="install expected homebrew packages")
    add_passthrough("redump-verifier", "verify dumps against redump")
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

    args, rest = parser.parse_known_args()
    if rest and args.command not in PASSTHROUGH:
        parser.error(f"unrecognized arguments: {' '.join(rest)}")
    try:
        match args.command:
            case "discord":
                asyncio.run(discord.main([]))
            case "host-mars":
                asyncio.run(host_mars.main([]))
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
            case "redump-verifier":
                asyncio.run(redump_verifier.main(rest))
            case "syncthing":
                asyncio.run(syncthing.main([]))
            case "update":
                asyncio.run(
                    update.main(args.skip, args.script, args.script_args)
                )
    except (errors.ProcessError, errors.UserError) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
