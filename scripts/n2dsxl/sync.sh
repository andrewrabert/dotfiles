#!/usr/bin/env sh
set -eu

YELLOW='\033[1;33m'
RESET_COLOR='\033[0m'

log() {
    printf '%b%s%b\n' "${YELLOW}" "$*" "${RESET_COLOR}"
}

case $# in
    0)
        SDCARD_DIR="/media/N2DSXL"
        ;;
    1)
        SDCARD_DIR="$1"
        ;;
    *)
        echo 'usage: [SDCARD_DIR]' >&2
        echo 'error: unexpected paramater(s)' >&2
        exit 1
        ;;
esac
if ! [ -d "${SDCARD_DIR}/Nintendo 3DS/2723a39ef3c87e55e9901f90eef310c1/" ]; then
    echo 'error: cannot determine source directory' >&2
    exit 1
fi

cd "${DOTFILES}/scripts/n2dsxl" || exit 1

src_hash="$(sha256sum ./sync-sol.sh | cut -d' ' -f1)"
dst_file="${SDCARD_DIR}/sync-sol.sh"
if [ ! -f "$dst_file" ] || [ "$src_hash" != "$(sha256sum "$dst_file" | cut -d' ' -f1)" ]; then
    log 'Copying sync-sol.sh'
    cp ./sync-sol.sh "$dst_file"
fi

log 'Syncing roms'
./sync-roms

log 'Backing up'
./backup-sol "${SDCARD_DIR}"
