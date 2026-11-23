# The root fs is usually read-only. zsh kept history in /tmp; fish cannot
# move its history file, so keep history in memory only.
set -g fish_history ''

# Add rw/ro status to prompt
function __pikvm_rw_status
    while read -l dev mnt fstype opts rest
        if test "$mnt" = /
            if string match -qr '(^|,)ro(,|$)' -- $opts
                printf '%s[ro]%s' (set_color yellow) (set_color normal)
            else
                printf '%s[rw]%s' (set_color red) (set_color normal)
            end
            return
        end
    end </proc/mounts
end
set -g --prepend dotfiles_prompt_prefix __pikvm_rw_status
