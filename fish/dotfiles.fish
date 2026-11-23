# fish entry point, ported from zsh/.zshenv (+ .zshrc via rc.fish, .zlogin
# via hosts/HOST/login.fish). Targets fish >= 4.0.
#
# full-update/60-fish links only this file into fish's own config dir:
#   ~/.config/fish/conf.d/dotfiles.fish -> $DOTFILES/fish/dotfiles.fish
# Everything else under ~/.config/fish stays local and fish-managed. The rest
# of this repo dir is reached through $DOTFILES, as zsh/ is.
#
# Local overrides (nothing here is tracked):
#   ~/.config/fish/conf.d/00-*.fish  before this file   (zsh: ~/.zshenv.local)
#                                    e.g. set -gx HOST_DOTFILES other-host
#   ~/.config/fish/config.fish       after all conf.d   (zsh: ~/.zshrc.local)
#   ~/.config/fish/completions/      extra completions
#
# Layout (mirrors zsh/):
#   dotfiles.fish          every shell         (zsh: .zshenv)
#   rc.fish                interactive shells  (zsh: .zshrc)
#   plugins/NAME/env.fish  every shell         (zsh: plugins/NAME/.zshenv)
#   plugins/NAME/rc.fish   interactive shells  (zsh: plugins/NAME/.zshrc)
#   hosts/HOST/env.fish    every shell         (zsh: hosts/HOST/.zshenv)
#   hosts/HOST/rc.fish     interactive shells  (zsh: hosts/HOST/.zshrc)
#   hosts/HOST/login.fish  login shells        (zsh: hosts/HOST/.zlogin)
#   hosts/HOST/functions/  autoloaded functions
#   completions/           completions         (zsh: functions/)

set -gx DOTFILES (path dirname (path dirname (path resolve (status filename))))
set -gx EDITOR nvim
set -gx LESSHISTFILE /dev/null
set -gx OPENER open

# an earlier conf.d file may already have set it
set -q HOST_DOTFILES[1]; or set -gx HOST_DOTFILES $hostname

for __dotfiles_plugin in $DOTFILES/fish/plugins/*/env.fish
    source $__dotfiles_plugin
end
set -e __dotfiles_plugin

# after local ~/.config/fish/completions, before vendor and generated ones
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
