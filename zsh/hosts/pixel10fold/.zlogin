if [ "$SHLVL" -eq 1 ] && [ -z "$TMUX" ] && command -v tmux-attach > /dev/null; then
    tmux-attach --no-detach --prompt && exit || true
fi
