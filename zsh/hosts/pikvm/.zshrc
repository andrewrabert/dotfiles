HISTFILE=/tmp/.zhistory-$USER

# Add rw/ro status to prompt
get_rw_status() {
    local line fields
    while IFS= read -r line; do
        fields=(${(s: :)line})
        if [[ $fields[2] == / ]]; then
            if [[ $fields[4] == ro,* || $fields[4] == *,ro,* || $fields[4] == *,ro ]]; then
                echo '[ro]'
            else
                echo '[rw]'
            fi
            return
        fi
    done < /proc/mounts
}

PROMPT='$(get_rw_status) '"$PROMPT"
