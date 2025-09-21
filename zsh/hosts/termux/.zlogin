if [ "$SHLVL" -eq 1 ] && [ -z "$TMUX" ] && command -v tmux-attach > /dev/null; then
	exec tmux-attach
fi
