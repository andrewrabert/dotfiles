#!/usr/bin/env zsh
repo=${0:A:h}

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
