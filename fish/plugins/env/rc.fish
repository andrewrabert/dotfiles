# Load a sh-style env file (KEY=value lines, `export`, comments) and export
# every variable it sets.
#
# zsh sourced the file with allexport. fish cannot source sh, so sh
# evaluates the file and every variable that comes out different is
# exported into fish. `unset` in the file has no effect here.

function __envload_usage
    printf '%s\n' 'usage: envload [--] [FILE]' '       ... | envload'
end

function envload
    argparse -n envload h/help -- $argv
    or begin
        __envload_usage >&2
        return 1
    end
    if set -q _flag_help
        __envload_usage
        return 0
    end

    set -l file
    switch (count $argv)
        case 0
            if isatty stdin
                echo 'error: no FILE and stdin is a tty' >&2
                __envload_usage >&2
                return 1
            end
            set file /dev/stdin
        case 1
            set file $argv[1]
            if not test -f $file
                echo 'error: argument is not a file' >&2
                return 1
            end
            # sh's `.` searches PATH for names without a slash
            string match -q -- '*/*' $file; or set file ./$file
        case '*'
            echo 'error: too many arguments' >&2
            __envload_usage >&2
            return 1
    end

    sh -c 'set -a; . "$1" >&2 || exit; env -0' envload $file | while read -lz pair
        set -l name (string replace -r '(?s)=.*' '' -- $pair)
        string match -qr '^[A-Za-z_][A-Za-z0-9_]*$' -- $name; or continue
        contains -- $name PWD OLDPWD SHLVL _; and continue
        set -l value "$(string replace -r '^[^=]*=' '' -- $pair)"
        if not set -q $name; or test "$$name" != "$value"
            set -gx $name $value
        end
    end
    return $pipestatus[1]
end
