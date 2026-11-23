# Repository names from the git-sync cache (the backup cache with -b/--backup)
function __gs_repos
    set -l cache_root $HOME/.cache
    test -n "$XDG_CACHE_HOME"; and set cache_root $XDG_CACHE_HOME
    set -l tokens (commandline -xpc)
    set -l cache_file $cache_root/git-sync
    if contains -- --backup $tokens; or contains -- -b $tokens
        set cache_file $cache_root/git-sync-backup
    end
    test -f $cache_file; and string match -rv '^$' <$cache_file
end

complete -c gs -f
complete -c gs -s b -l backup -d 'Use backup cache'
complete -c gs -s c -l clone-from-backup -d 'Clone from backup to regular location'
complete -c gs -a '(__gs_repos)'
