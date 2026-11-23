if command -q pi
    function pi
        PI_SKIP_VERSION_CHECK=1 command pi $argv
    end
end
