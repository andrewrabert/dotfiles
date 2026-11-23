#!/usr/bin/env zsh
if (( $# != 1 )); then
    echo "usage: ${0:t} HOST" >&2
    exit 2
fi

host=$1
file=~/.zshenv.local

touch $file || exit
lines=("${(@f)$(grep -v '^export HOST_DOTFILES=' $file)}")
lines=(${lines:#} "export HOST_DOTFILES=${(q)host}")
print -rl -- $lines >$file || exit
echo "$file: HOST_DOTFILES=$host"
