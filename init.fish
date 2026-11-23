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

$repo/link_fish.fish; or exit
$repo/install_py_dotfiles.sh; or exit
