#!/usr/bin/env zsh
if (( $# > 1 )); then
    echo "usage: ${0:t} [HOST]" >&2
    exit 2
fi

repo=${0:A:h}

if (( $# == 1 )); then
    host=$1
    file=~/.zshenv.local

    touch $file || exit
    lines=("${(@f)$(grep -v '^export HOST_DOTFILES=' $file)}")
    lines=(${lines:#} "export HOST_DOTFILES=${(q)host}")
    print -rl -- $lines >$file || exit
    echo "$file: HOST_DOTFILES=$host"
fi

bin_dir=${XDG_DATA_HOME:-$HOME/.local/share}/bertbox/bin
bertbox=$bin_dir/bertbox
if [[ ! -e $bertbox ]]; then
    $repo/install_bertbox.sh || exit
fi

for name in .zshenv .zshrc; do
    ln -sf $repo/zsh/$name ~/$name || exit
    echo "$HOME/$name -> $repo/zsh/$name"
done
$repo/install_py_dotfiles.sh || exit
