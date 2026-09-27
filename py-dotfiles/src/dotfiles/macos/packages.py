import shutil

from . import homebrew

EXPECTED_PACKAGES = {
    "advancecomp",
    "aria2",
    "ast-grep",
    "bat",
    "coreutils",
    "curl",
    "curlie",
    "dash-shell",
    "diffutils",  # added mainly so zsh diff completion completes second path
    "exiftool",
    "exiv2",
    "fd",
    "font-hack",
    "font-hack-nerd-font",
    "fzf",
    "gifsicle",
    "git",
    "gnu-sed",
    "gnu-tar",
    "htop",
    "hyperfine",
    "imagemagick",
    "innoextract",
    "iperf3",
    "jpegoptim",
    "jq",
    "moreutils",
    "neovim",
    "node",
    "openssh",
    "oxipng",
    "pandoc",
    "prettier",
    "ripgrep",
    "rsync",
    "ruff",
    "sevenzip",  # aka _the_ 7zip
    "shellcheck",
    "stylua",
    "tmux",
    "tree-sitter-cli",
    "ty",
    "unzip",
    "uv",
    "vips",
    "yazi",
    "zip",
    "zsh",
    "zstd",
}


async def main():
    installed = await homebrew.Homebrew.get_installed()
    expected = EXPECTED_PACKAGES.copy()

    # Add docker-completion if docker is available
    if shutil.which("docker"):
        expected.add("docker-completion")

    missing = expected - installed
    if missing:
        await homebrew.Homebrew.install(missing)
