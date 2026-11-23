# Non-hidden entries of every $DOTFILES*/full-update directory
function __full_update_scripts
    for var in (set -n | string match -- 'DOTFILES*')
        set -l dir $$var/full-update
        test -d "$dir"; and path basename -- $dir/*
    end
end

complete -c full-update -f -a '(__full_update_scripts)'
