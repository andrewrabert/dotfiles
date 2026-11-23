# when the previous command exits with a code != 0,
# show it on a new line
function __dotfiles_exit_status --on-event fish_postexec
    set -l exit_status $status
    if test $exit_status -gt 0
        set_color red
        echo $exit_status
        set_color normal
    end
end
