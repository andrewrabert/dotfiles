# start a subshell in a temporary directory
# delete the directory when the subshell exists
temp-context() {
    (
        if [ -v zsh_temp_context ]; then
            echo 'error: cannot create nested temp-context' >&2
            return 1
        fi
        local usage='usage: temp-context [PREFIX]'
        local name="zsh-$$-temp-context"
        while [ $# -gt 1 ]; do
            case "$1" in
                --)
                    shift
                    break
                    ;;
                -h|--help)
                    echo "$usage"
                    return 0
                    ;;
                -*)
                    echo "$usage" >&2
                    echo 'error: invalid argument' >&2
                    return 1
                    ;;
                *)
                    break
                    ;;
            esac
        done
        case $# in
            0)
                ;;
            1)
                if [ "$1" != "${1:t}" ]; then
                    echo 'error: not a valid basename' >&2
                    return 1
                fi
                name="${1}.${name}"
                ;;
            *)
                echo "$usage" >&2
                return 1
                ;;
        esac

        # always use tmp for ease of typing
        local tmpdir='/tmp'
        if [ -z "$tmpdir" ]; then
            echo "error: cannot find valid tmpdir parent dir" >&2
            return 1
        fi

        readonly zsh_temp_context="${tmpdir}/${name}"
        cleanup() { rm -rf "$zsh_temp_context" };
        trap cleanup EXIT;
        mkdir "$zsh_temp_context"
        cd "$zsh_temp_context"
        _zsh_temp_context="$zsh_temp_context" zsh
    )
}

if [ -v _zsh_temp_context ]; then
    readonly temp_context="$_zsh_temp_context"
    readonly zsh_temp_context="$_zsh_temp_context"
    unset _zsh_temp_context
    PROMPT="(temp_context)${PROMPT}"
fi
