if command -q fzf
    # CTRL-T - Insert the selected file path(s) at the cursor
    function __dotfiles_fzf_file_widget
        set -l items (command fd -0 | FZF_DEFAULT_OPTS="--height 40% --reverse $FZF_DEFAULT_OPTS" fzf -m --read0 --print0 | string split0)
        if set -q items[1]
            commandline -i -- (string join ' ' -- (string escape -- $items))' '
        end
        commandline -f repaint
    end
    bind -M insert ctrl-t __dotfiles_fzf_file_widget

    # ALT-C - cd into the selected directory
    function __dotfiles_fzf_cd_widget
        set -l dir (command fd -t d | FZF_DEFAULT_OPTS="--height 40% --reverse $FZF_DEFAULT_OPTS" fzf +m)
        if test -z "$dir"
            commandline -f repaint
            return 0
        end
        if test -z "$(commandline)"
            # Run cd from the command line so it lands in history
            commandline -r -- "builtin cd -- "(string escape -- $dir)
            commandline -f execute
        else
            # Keep the pending command line (zsh: push-line)
            builtin cd -- $dir
            commandline -f repaint
        end
    end
    bind -M insert alt-c __dotfiles_fzf_cd_widget

    # CTRL-R - Replace the command line with the selected history entry
    function __dotfiles_fzf_history_widget
        set -l selected (history -z | FZF_DEFAULT_OPTS="--height 40% $FZF_DEFAULT_OPTS" fzf --scheme=history --bind=ctrl-r:toggle-sort +m --read0 --print0 --query="$(commandline)" | string split0)
        if test -n "$selected"
            commandline -r -- $selected
            commandline -C (string length -- "$selected")
        end
        commandline -f repaint
    end
    bind -M insert ctrl-r __dotfiles_fzf_history_widget
end
