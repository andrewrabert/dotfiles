#!/bin/sh
# Download the bertbox binary from CI and run its `install bertbox` command.
# With --output PATH, only save the binary to PATH.
set -eu

die() {
    echo "install_bertbox.sh: $*" >&2
    exit 1
}

download() {
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL -o "$2" "$1"
    elif command -v wget >/dev/null 2>&1; then
        wget -q -O "$2" "$1"
    else
        die "need curl or wget to download $1"
    fi
}

extract_zip() {
    if command -v unzip >/dev/null 2>&1; then
        unzip -q -o "$1" -d "$2"
    elif command -v bsdtar >/dev/null 2>&1; then
        bsdtar -xf "$1" -C "$2"
    elif command -v python3 >/dev/null 2>&1; then
        python3 -I -m zipfile -e "$1" "$2"
    elif command -v busybox >/dev/null 2>&1; then
        busybox unzip -q -o "$1" -d "$2"
    else
        die "need unzip, bsdtar, python3, or busybox to extract $1"
    fi
}

usage() {
    echo "usage: install_bertbox.sh [--output PATH]" >&2
    exit 2
}

out=
while [ $# -gt 0 ]; do
    case "$1" in
        -o | --output)
            [ $# -ge 2 ] || usage
            out=$2
            shift 2
            ;;
        *) usage ;;
    esac
done

system=$(uname -s)
machine=$(uname -m)
case "$machine" in
    arm64) arch=aarch64 ;;
    *) arch=$machine ;;
esac
case "$system" in
    Linux)
        if command -v termux-info >/dev/null 2>&1; then
            os=linux-android
        elif ls /lib/ld-musl-* >/dev/null 2>&1; then
            os=unknown-linux-musl
        else
            os=unknown-linux-gnu
        fi
        ;;
    Darwin) os=apple-darwin ;;
    *) os=$system ;;
esac
target=$arch-$os
case "$target" in
    x86_64-unknown-linux-gnu | aarch64-unknown-linux-gnu | \
        x86_64-unknown-linux-musl | aarch64-unknown-linux-musl | \
        aarch64-linux-android | \
        x86_64-apple-darwin | aarch64-apple-darwin) ;;
    *) die "unsupported platform: $system $machine" ;;
esac

scratch=$(mktemp -d "${TMPDIR:-/tmp}/bertbox-download.XXXXXX")
trap 'rm -rf "$scratch"' EXIT
trap 'exit 1' HUP INT TERM

url="https://nightly.link/andrewrabert/tools/workflows/ci/main/bertbox-$target.zip"
echo "Downloading $url"
download "$url" "$scratch/bertbox.zip"
extract_zip "$scratch/bertbox.zip" "$scratch"
chmod +x "$scratch/bertbox"
if [ -n "$out" ]; then
    mv "$scratch/bertbox" "$out"
else
    "$scratch/bertbox" install bertbox
fi
