if command -v rg > /dev/null; then
    alias rg="rg --ignore-case --hidden --glob '!\.git/'"

    function rgnvim() {
        files=($(rg --files-with-matches --null "$@" | sort | tr '\0' '\n'))
        # Check if any files were found
        if (( ${#files[@]} == 0 )); then
            echo "No matches found"
            return 1
        fi
        nvim "${files[@]}"
    }
fi
