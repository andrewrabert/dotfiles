if command -v rg > /dev/null; then
    alias rg="rg --ignore-case --hidden --glob '!\.git/'"

    function rge() {
        local -a files
        files=(${(0o)"$(rg --files-with-matches --null "$@")"})
        # Check if any files were found
        if (( ${#files[@]} == 0 )); then
            echo "No matches found"
            return 1
        fi
        "$EDITOR" -- "${files[@]}"
    }
fi
