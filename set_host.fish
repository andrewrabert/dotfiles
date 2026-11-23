#!/usr/bin/env fish
if test (count $argv) -ne 1
    echo "usage: "(status basename)" HOST" >&2
    exit 2
end

set host $argv[1]
set conf_d $__fish_config_dir/conf.d
set file $conf_d/00-host.fish

mkdir -p $conf_d; or exit
echo "set -gx HOST_DOTFILES "(string escape -- $host) >$file; or exit
echo "$file: HOST_DOTFILES=$host"
