if (( $+commands[fzf] )); then
    # CTRL-T - Paste the selected file path(s) into the command line
    fzf-file-widget() {
        setopt localoptions pipefail
        local -a items
        items=("${(@0)$(command fd -0 | FZF_DEFAULT_OPTS="--height 40% --reverse $FZF_DEFAULT_OPTS" fzf -m --read0 --print0)}")
        local ret=$?
        items=("${(@)items:#}")
        if (( $#items )); then
            LBUFFER+="${(j: :)${(@q)items}} "
        fi
        zle reset-prompt
        return ret
    }
    zle     -N   fzf-file-widget
    bindkey '^T' fzf-file-widget

    # ALT-C - cd into the selected directory
    fzf-cd-widget() {
        setopt localoptions pipefail
        local dir
        dir="$(command fd -t d | FZF_DEFAULT_OPTS="--height 40% --reverse $FZF_DEFAULT_OPTS" fzf +m)"
        if [[ -z "$dir" ]]; then
            zle redisplay
            return 0
        fi
        # Run cd via accept-line so precmd/chpwd hooks fire and it lands in history
        zle push-line
        BUFFER="builtin cd -- ${(q)dir}"
        zle accept-line
        local ret=$?
        zle reset-prompt
        return ret
    }
    zle     -N    fzf-cd-widget
    bindkey '\ec' fzf-cd-widget

    # CTRL-R - Paste the selected command from history into the command line
    fzf-history-widget() {
        setopt localoptions noglobsubst noposixbuiltins pipefail
        local selected
        selected="$(fc -rl 1 | FZF_DEFAULT_OPTS="--height 40% $FZF_DEFAULT_OPTS -n2..,.. --scheme=history --bind=ctrl-r:toggle-sort --query=${(qqq)LBUFFER} +m" fzf)"
        local ret=$?
        local num="${${selected## #}%% *}"
        if [[ "$num" == <-> ]]; then
            zle vi-fetch-history -n $num
        fi
        zle reset-prompt
        return ret
    }
    zle     -N   fzf-history-widget
    bindkey '^R' fzf-history-widget
fi
