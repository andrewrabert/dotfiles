function up
    set -l n 1
    set -q argv[1]; and set n $argv[1]
    set -l target (string repeat -n $n ../)
    if isatty stdout
        cd $target
    else
        echo -n $target
    end
end
