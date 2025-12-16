claude() {
    if [ ! -f "CLAUDE.local.md" ]; then
        if claude-link-memory --show-path > /dev/null 2>&1; then
            claude-link-memory
        fi
    fi
    command claude "${@}"
}
