function localbin
    mkdir -p ~/.local/bin
    set -l _source
    set -l _target

    switch (count $argv)
        case 2
            set _source (path resolve -- $argv[1])
            set _target $argv[2]
        case 1
            set _source (path resolve -- $argv[1])
            set _target (path basename -- $_source)
        case '*'
            echo 'error: missing/extra argument(s)' >&2
            return 1
    end

    ln --force --symbolic --no-target-directory $_source ~/.local/bin/$_target
end
