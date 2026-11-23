if command -v go > /dev/null; then
    export GOPATH=~/.local/share/go
    path=(
        "${GOPATH}/bin"
        "$path[@]"
    )
fi
