__proton="$(command -v proton)"
if [ -z "$__proton" ]; then
    unset __proton
else
    proton() {
        local cd_prefix
        local prefix
        local -a args
        prefix=default
        while [ $# -gt 0 ]; do
            case "$1" in
                --cd)
                    cd_prefix=1
                    shift
                    ;;
                -p|--prefix)
                    args+=("$1")
                    shift
                    prefix="$1"
                    args+=("$prefix")
                    shift
                    ;;
                --)
                    while [ $# -gt 0 ]; do
                        args+=("$1")
                        shift
                    done
                    ;;
                *)
                    args+=("$1")
                    shift
                    ;;
            esac
        done
        if [ -n "$cd_prefix" ]; then
            cd "$("$__proton" --prefix "$prefix")/pfx/drive_c"
        fi
        "$__proton" "${args[@]}"
    }
fi
