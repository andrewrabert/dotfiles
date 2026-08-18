#!/usr/bin/env sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

case $# in
    0)
        SOURCE="${SCRIPT_DIR}"
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

ROM_DIR="$(cd "${SOURCE}/Roms/PICO" && pwd)"
cd "${ROM_DIR}"
mkdir -p .Imgs
for f in *.png; do
    DEST="${ROM_DIR}/.Imgs/$(basename "$f")"
    if ! [ -f "$DEST" ]; then
        printf 'Generating thumbnail for %s\n' "$f"
        "${SCRIPT_DIR}/generate_thumbnail.py" --pico8 --output "${DEST}" "$f"
    fi
done
