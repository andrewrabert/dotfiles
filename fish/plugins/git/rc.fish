if command -q git
    function gl
        git log --oneline $argv
    end

    # zsh: print -s
    function __gs_history
        history append -- (string join ' ' -- $argv) 2>/dev/null
    end

    function gs
        argparse -n gs -i u/update b/backup c/clone-from-backup -- $argv
        or return 1

        if set -q _flag_update
            git-sync --build-cache
        end

        # If --clone-from-backup is set, select from backup cache and clone to regular location
        if set -q _flag_clone_from_backup
            set -l regular_target (git-sync --show-backup-cache | sed 's|^backup/||' | fzf --tac --exact --no-sort)
            if test -z "$regular_target"
                return 130
            end

            set -l backup_target "backup/$regular_target"

            # Get the backup repo directory to extract origin URL
            set -l backup_repo_dir (git-sync $backup_target)
            if test -z "$backup_repo_dir"; or not test -d "$backup_repo_dir"
                echo "error: backup repository not found: $backup_target" >&2
                return 1
            end

            # Get origin URL from backup repo
            set -l origin_url (git -C $backup_repo_dir remote get-url origin 2>/dev/null)
            if test -z "$origin_url"
                echo 'error: no origin found in backup repository' >&2
                return 1
            end

            # Clone to regular location
            set -l repo_dir (git-sync $regular_target)
            if test -n "$repo_dir"
                __gs_history gs --clone-from-backup
                cd $repo_dir
                return
            end
            return 0
        end

        # If first arg is a flag (for git-sync), pass through
        if string match -q -- '-*' "$argv[1]"
            git-sync $argv
            return
        end

        set -l target
        switch (count $argv)
            case 0
                if set -q _flag_backup
                    set target (git-sync --show-backup-cache | sed 's|^backup/||' | fzf --tac --exact --no-sort)
                    if test -z "$target"
                        return 130
                    end
                    set target "backup/$target"
                else
                    set target (git-sync --show-cache | fzf --tac --exact --no-sort)
                    if test -z "$target"
                        return 130
                    end
                end
            case 1
                set target $argv[1]
                if set -q _flag_backup; and not string match -q -- 'backup/*' $target
                    set target "backup/$target"
                end
            case '*'
                echo 'error: unexpected arguments' >&2
                return 1
        end

        if not isatty stdout
            git-sync $target
            return
        end

        if set -q _flag_backup
            __gs_history gs --backup $target
        else
            __gs_history gs $target
        end
        set -l repo_dir (git-sync $target)
        if test -z "$repo_dir"
            return 130
        end
        cd $repo_dir
    end

    function gsb
        set -l target (git-sync --show-backup-cache | sed 's|^backup/||' | fzf --tac --exact --no-sort)
        if test -z "$target"
            return 130
        end
        __gs_history gs $target
        gs $target
    end
end
