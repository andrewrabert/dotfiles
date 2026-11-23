localbin() {
    mkdir -p ~/.local/bin
    local _source
    local _target

    case $# in
        2)
            _source="$1:A"
            _target="$2"
            ;;
        1)
            _source="$1:A"
            _target="${_source##*/}"
            ;;
        *)
            echo 'error: missing/extra argument(s)' >&2
            return 1
    esac

    ln --force --symbolic --no-target-directory "$_source" ~/.local/bin/"$_target"
}
