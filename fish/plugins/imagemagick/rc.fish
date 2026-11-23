if command -q magick
    function convert
        echo 'ERROR: The convert command is deprecated in IMv7, use "magick" or "magick convert"' >&2
        return 1
    end
end
