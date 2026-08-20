#!/usr/bin/env sh
set -eu

YELLOW='\033[1;33m'
RESET_COLOR='\033[0m'

log() {
    printf '%b%s%b\n' "${YELLOW}" "$*" "${RESET_COLOR}"
}

case $# in
    0)
        SDCARD_DIR="/run/media/$(id -un)/RGROTATE"
        ;;
    1)
        SDCARD_DIR="$1"
        ;;
    *)
        echo 'usage: [SDCARD_DIR]' >&2
        echo 'error: unexpected parameter(s)' >&2
        exit 1
        ;;
esac
if ! [ -d "${SDCARD_DIR}/Roms" ]; then
    echo 'error: cannot determine source directory' >&2
    exit 1
fi

cd "${DOTFILES}/scripts/rgrotate" || exit 1

log 'Syncing roms'
./sync_roms.py --delete "${SDCARD_DIR}"
