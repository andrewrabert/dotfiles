if [ -n "$BASE16_SHELL" ]; then
    if [ -z "$SSH_CONNECTION" ] && [ -z "$TMUX" ] && [ -f ~/.base16_theme ]; then
        . ~/.base16_theme
    fi
fi
