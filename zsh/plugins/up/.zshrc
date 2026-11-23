up() {
    local target="$(printf -- '../%.0s' {1..$1})"
    if [[ -t 1 ]] then
        cd "$target"
    else
        echo -n "$target"
    fi
}
