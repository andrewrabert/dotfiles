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
    noted,
    syncthing,
    zoekt_simple,
)


def add_force(parser, help):
    parser.add_argument("-f", "--force", action="store_true", help=help)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    bertbox_parser = subparsers.add_parser("bertbox", help="Manage bertbox")
    add_force(bertbox_parser, "skip the ETag check and reinstall")

    bxwrp_parser = subparsers.add_parser("bxwrp", help="Manage bxwrp")
    add_force(bxwrp_parser, "skip the commit check and rebuild")

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
    subparsers.add_parser("macos", help="install expected homebrew packages")

    noted_parser = subparsers.add_parser("noted", help="Manage noted")
    add_force(noted_parser, "skip the ETag check and reinstall")

    subparsers.add_parser("syncthing", help="write .stignore includes")
    subparsers.add_parser("zoekt-simple", help="Manage zoekt-simple")

    args = parser.parse_args()
    try:
        match args.command:
            case "bertbox":
                asyncio.run(bertbox.main(force=args.force))
            case "bxwrp":
                asyncio.run(bxwrp.main(force=args.force))
            case "discord":
                discord.main()
            case "host-mars":
                asyncio.run(host_mars.main())
            case "jellium-desktop":
                asyncio.run(jellium_desktop.main(args.platform, args.ssh))
            case "kde":
                from dotfiles import kde

                asyncio.run(kde.settings.main())
            case "kde-color-schemes":
                from dotfiles import kde

                asyncio.run(kde.color_schemes.main())
            case "krita":
                asyncio.run(krita.main())
            case "macos":
                from dotfiles import macos

                asyncio.run(macos.packages.main())
            case "noted":
                asyncio.run(noted.main(force=args.force))
            case "syncthing":
                syncthing.main()
            case "zoekt-simple":
                zoekt_simple.main()
    except (errors.ProcessError, errors.UserError) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
