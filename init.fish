#!/usr/bin/env fish
set repo (path dirname (path resolve (status filename)))

set data_home ~/.local/share
test -n "$XDG_DATA_HOME"; and set data_home $XDG_DATA_HOME
set bin_dir $data_home/bertbox/bin
set bertbox $bin_dir/bertbox
if not test -e $bertbox
    mkdir -p $bin_dir; or exit
    $repo/download_bertbox.sh $bertbox; or exit
end

set name dotfiles.fish
set conf_d $__fish_config_dir/conf.d
set target $repo/fish/$name
set link $conf_d/$name

mkdir -p $conf_d; or exit
ln -sf $target $link; or exit
echo "$link -> $target"
