set -gx DOTFILES (path dirname (path dirname (path resolve (status filename))))
set -gx EDITOR nvim
set -gx LESSHISTFILE /dev/null
set -gx OPENER open

set -q HOST_DOTFILES[1]; or set -gx HOST_DOTFILES $hostname

for __dotfiles_plugin in $DOTFILES/fish/plugins/*/env.fish
    source $__dotfiles_plugin
end
set -e __dotfiles_plugin

set -l i (contains -i -- $__fish_config_dir/completions $fish_complete_path)
if set -q i[1]
    set -g fish_complete_path $fish_complete_path[1..$i] $DOTFILES/fish/completions $fish_complete_path[(math $i + 1)..-1]
else
    set -g --prepend fish_complete_path $DOTFILES/fish/completions
end

set -l data_home $HOME/.local/share
test -n "$XDG_DATA_HOME"; and set data_home $XDG_DATA_HOME
fish_add_path -Pm $DOTFILES/.local/bin $data_home/bertbox/bin
if status is-interactive; and test -r $data_home/bertbox/fish/bertbox.fish
    source $data_home/bertbox/fish/bertbox.fish
end

set -l host_dir $DOTFILES/fish/hosts/$HOST_DOTFILES
if test -r $host_dir/env.fish
    source $host_dir/env.fish
end

fish_add_path -Pm ~/.local/bin

if status is-interactive
    source $DOTFILES/fish/rc.fish
end

if status is-login; and test -r $host_dir/login.fish
    source $host_dir/login.fish
end
