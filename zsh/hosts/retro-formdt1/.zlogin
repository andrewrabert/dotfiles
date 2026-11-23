if [ "$XDG_VTNR" -eq 1 ] && [ -z "$TMUX" ] && ! pidof tmux > /dev/null && command -v tmux-attach > /dev/null; then
	exec tmux-attach
fi
