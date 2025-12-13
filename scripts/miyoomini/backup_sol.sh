#!/usr/bin/env sh
# system IDs:
#   314EADC0CA5A : MMv4.1
#   C2A037C6B080 : MMv4 (RTC modded)
#   D7C3FDF55222 : MM+ (RTC modded)
set -eu

case $# in
    0)
        SOURCE="$(dirname "$0")"
        ;;
    1)
        SOURCE="$1"
        ;;
    *)
        echo 'usage: [SDCARD_DIR]' >&2
        echo 'error: unexpected argument(s)' >&2
        exit 1
        ;;
esac
if ! [ -f "${SOURCE}/.tmp_update/onionVersion/version.txt" ]; then
    echo 'error: cannot determine source directory' >&2
    exit 1
fi

TARGET='/storage/Backup/MiyooMini_Onion'
if ! [ -d "${TARGET}" ]; then
    TARGET="sol:${TARGET}"
fi

# Updating Onion OS might remove the overclock for RetroArch.
# 1500mhz is stable on both my MMv4 and MM+ and is needed for smoothly playing:
#  - Final Fantasy VI (mGBA)
#  - Pokemon Unbound (mGBA)
if [ "$(cat "${SOURCE}/RetroArch/cpuclock.txt" 2> /dev/null)" != '1500' ]; then
    echo 'writing RetroArch overclock file (1500mhz)' >&2
    echo 1500 > "${SOURCE}/RetroArch/cpuclock.txt"
fi

rsync -avz \
    --delete \
    --progress \
    --exclude 'Roms/NDS/*.nds' \
    --exclude 'Roms/PS/*/*.bin' \
    "${SOURCE}/" "${TARGET}"
