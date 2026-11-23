envload() {
    setopt localoptions allexport
    usage() { print -u${1:-2} "usage: envload [--] [FILE]\n       ... | envload" }
    local file
    while (( $# )); do
        case "$1" in
            -h|--help) usage 1; return 0 ;;
            --) shift; [[ $# == 1 ]] || { usage; return 1 }; file="$1"; break ;;
            -*) print -u2 "error: invalid option: $1"; usage; return 1 ;;
            *)
                [[ $# -eq 1 ]] || { print -u2 "error: missing required argument"; return 1 }
                file="$1"
                [[ -f "$file" ]] || { print -u2 "error: argument is not a file"; return 1 }
        esac
        shift
    done
    if [[ -z "$file" ]]; then
        [[ ! -t 0 ]] || { print -u2 "error: no FILE and stdin is a tty"; usage; return 1 }
        file=/dev/stdin
    fi
    source "$file"
}
