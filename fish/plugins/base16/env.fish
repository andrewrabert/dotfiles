if test -d ~/.local/share/base16-shell
    set -gx BASE16_SHELL ~/.local/share/base16-shell
    set -gx BASE16_SHELL_HOOKS $DOTFILES/base16_shell_hooks
else
    set -e BASE16_SHELL
end
