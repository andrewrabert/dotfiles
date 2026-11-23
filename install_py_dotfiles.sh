#!/bin/sh
set -eu

repo=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
uv tool install --reinstall --upgrade -e "$repo/py-dotfiles"
