if command -v pnpm > /dev/null; then
    path=(
        ~/.local/share/pnpm/bin
        "$path[@]"
    )
fi
