if command -q rg
    alias rg "rg --ignore-case --hidden --glob '!\.git/'"

    function rge
        set -l files (rg --files-with-matches --null $argv | sort -z | string split0)
        if not set -q files[1]
            echo 'No matches found'
            return 1
        end
        $EDITOR -- $files
    end
end
