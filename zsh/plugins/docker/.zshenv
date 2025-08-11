if [ -d "$HOME/.docker/bin" ]; then
    path=(
        "$HOME/.docker/bin"
        "$path[@]"
    )
fi
