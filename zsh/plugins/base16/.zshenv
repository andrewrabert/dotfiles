export BASE16_SHELL=~/.local/share/base16-shell
if [ -d "$BASE16_SHELL" ]; then
    export BASE16_SHELL_HOOKS="$DOTFILES/base16_shell_hooks"
else
    unset BASE16_SHELL
fi
