#!/usr/bin/env fish
set repo (path dirname (path resolve (status filename)))

set name dotfiles.fish
set conf_d $__fish_config_dir/conf.d
set target $repo/fish/$name
set link $conf_d/$name

mkdir -p $conf_d; or exit
ln -sf $target $link; or exit
echo "$link -> $target"
