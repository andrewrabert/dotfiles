function zwatch
    set -l sleeptime 2
    set -l help 'usage: zwatch [-n TIMEOUT] command'

    if test "$argv[1]" = -n
        set sleeptime $argv[2]
        set -e argv[1..2]
    else if contains -- "$argv[1]" --help -h
        echo $help
        return 0
    else if test -z "$argv[1]"
        echo $help >&2
        return 1
    end
    while true
        clear
        echo (date +'%Y-%m-%d %H:%M:%S')" sleep $sleeptime""s: $argv" | cut -c1-$COLUMNS
        echo
        # zsh ran this in a subshell; fish has none, so e.g. a `cd` sticks.
        eval $argv
        sleep $sleeptime
    end
end
