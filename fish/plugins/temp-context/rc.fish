# start a nested fish in a temporary directory
# delete the directory when that shell exits
function temp-context
    if set -q fish_temp_context
        echo 'error: cannot create nested temp-context' >&2
        return 1
    end
    set -l usage 'usage: temp-context [PREFIX]'
    argparse -n temp-context h/help -- $argv
    or begin
        echo $usage >&2
        return 1
    end
    if set -q _flag_help
        echo $usage
        return 0
    end

    set -l name "fish-$fish_pid-temp-context"
    switch (count $argv)
        case 0
        case 1
            if test "$argv[1]" != "$(path basename -- $argv[1])"
                echo 'error: not a valid basename' >&2
                return 1
            end
            set name "$argv[1].$name"
        case '*'
            echo $usage >&2
            return 1
    end

    # always use tmp for ease of typing
    set -l dir /tmp/$name
    mkdir $dir; or return
    _fish_temp_context=$dir fish -C "cd $(string escape -- $dir)"
    set -l ret $status
    rm -rf -- $dir
    return $ret
end

if set -q _fish_temp_context
    set -g temp_context $_fish_temp_context
    set -g fish_temp_context $_fish_temp_context
    set -e _fish_temp_context

    function __temp_context_prompt
        printf '(temp_context)'
    end
    set -g --prepend dotfiles_prompt_prefix __temp_context_prompt
end
