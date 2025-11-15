HISTFILE=/tmp/.zhistory-$USER

# Add rw/ro status to prompt
get_rw_status() {
    local line
    while IFS= read -r line; do
        if [[ $line == ' / '* ]]; then
            if [[ $line == *' ro'* || $line == *' ro,'* ]]; then
                echo '[ro]'
            else
                echo '[rw]'
            fi
            return
        fi
    done < /proc/mounts
}

PROMPT='$(get_rw_status) '"$PROMPT"
