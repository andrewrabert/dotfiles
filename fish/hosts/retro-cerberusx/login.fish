if test "$XDG_VTNR" = 1; and test -z "$TMUX"; and not pidof tmux >/dev/null; and command -q tmux-attach
    exec tmux-attach
end
