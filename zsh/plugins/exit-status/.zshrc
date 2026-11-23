exit_status () {
    # when the previous command exits with a code != 0,
    # show it on a new line
    local exit_status=$?
    if [[ $exit_status -gt 0 ]]; then
        echo -e "${fg[red]}${exit_status}${reset_color}"
    fi
}

add-zsh-hook precmd exit_status
