# Host entries from ~/.ssh/config, without wildcard patterns
function __ssh_tmux_attach_hosts
    test -f ~/.ssh/config; or return
    string replace -rf '^\s*[Hh]ost\s+' '' <~/.ssh/config \
        | string match -ar '\S+' \
        | string match -rv '[*?]'
end

complete -c ssh-tmux-attach -f
complete -c ssh-tmux-attach -s n -l new-tab -d 'Create new tmux tab'
complete -c ssh-tmux-attach -s h -l help -d 'Show help message'
complete -c ssh-tmux-attach -n __fish_use_subcommand -a '(__ssh_tmux_attach_hosts)' -d 'SSH host'
