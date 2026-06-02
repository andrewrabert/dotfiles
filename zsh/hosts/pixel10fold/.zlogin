if [ "$SHLVL" -eq 1 ] && [ -z "$TMUX" ] && command -v tmux-attach > /dev/null; then
    while true; do
	    tmux-attach --no-detach --prompt
    done
fi
