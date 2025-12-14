#!/usr/bin/env sh
set -eu
SOURCE="$(dirname "$0")"
exec "${DOTFILES}/scripts/miyoomini/sync.sh" "${SOURCE}"
