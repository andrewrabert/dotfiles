#!/usr/bin/env sh
set -eu
SOURCE="$(dirname "$0")"
exec "${DOTFILES}/scripts/n2dsxl/sync.sh" "${SOURCE}"
