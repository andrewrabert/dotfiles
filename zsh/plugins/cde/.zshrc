# cd to the path output by a command
cde() {
    local loc
    local ret
    loc="$("$@")"
    ret=$?
    if [ "$ret" -ne 0 ]; then
        return "$ret"
    fi
    if [ -f "$loc" ]; then
        loc="${loc%/*}/"
    fi
    echo "$loc"
    cd "$loc"
}
