# cd to the path output by a command
function cde
    set -l loc "$($argv)"
    or return
    if test -f "$loc"
        set loc (path dirname -- $loc)/
    end
    echo $loc
    cd $loc
end
