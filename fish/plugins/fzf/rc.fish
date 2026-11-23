if functions -q fzf_key_bindings
    set -g FZF_CTRL_T_COMMAND fd
    fzf_key_bindings
end
