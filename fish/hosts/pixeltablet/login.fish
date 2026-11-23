if test "$SHLVL" = 1; and test -z "$TMUX"; and command -q tmux-attach
    while true
        tmux-attach --prompt
    end
end
