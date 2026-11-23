if command -q yazi
    function y
        set -l tmp (mktemp -t yazi-cwd.XXXXXX)
        yazi --cwd-file=$tmp $argv
        set -l cwd "$(command cat -- $tmp)"
        if test -n "$cwd"; and test "$cwd" != "$PWD"
            builtin cd -- $cwd
        end
        rm -f -- $tmp
    end
end
