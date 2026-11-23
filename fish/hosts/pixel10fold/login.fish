if test "$SHLVL" = 1; and test -z "$TMUX"; and command -q tmux-attach
    tmux-attach --no-detach --prompt; and exit
end
