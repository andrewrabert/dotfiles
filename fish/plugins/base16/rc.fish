if set -q BASE16_SHELL
    if test -z "$SSH_CONNECTION"; and test -z "$TMUX"; and test -f ~/.base16_theme.fish
        # Presetting TTY stops the theme running `tty` to find the terminal.
        TTY=/dev/tty source ~/.base16_theme.fish
    end
end
