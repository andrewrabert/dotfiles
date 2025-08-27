if command -v direnv > /dev/null; then
    eval "$(direnv hook zsh)"

    direnv_indicator() {
        if [ -z "$DIRENV_DIR" ]; then
            unset prompt_direnv
        else
            prompt_direnv="(direnv)"
        fi
    }

    add-zsh-hook precmd direnv_indicator

    PROMPT='$prompt_direnv'"$PROMPT"
fi
