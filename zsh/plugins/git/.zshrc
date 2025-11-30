if command -v git > /dev/null; then
    gs() {
        local only_remote=0
        local update_cache=0
        local use_backup=0
        local use_clone_from_backup=0
        local -a args

        # Parse flags
        for arg in "$@"; do
            case "$arg" in
                --create)
                    args+=("--create")
                    ;;
                -u|--update)
                    update_cache=1
                    ;;
                -b|--backup)
                    use_backup=1
                    ;;
                -c|--clone-from-backup)
                    use_clone_from_backup=1
                    ;;
                -r|--remote)
                    only_remote=1
                    ;;
                -*)
                    if [[ $all_recognized -eq 0 ]]; then
                        echo "error: unrecognized flag: $arg" >&2
                        return 1
                    fi
                    ;;
                *)
                    args+=("$arg")
                    ;;
            esac
        done

        if [[ $update_cache -eq 1 ]]; then
            git-sync --build-cache --remote
        fi

        # If --clone-from-backup is set, select from backup cache and clone to regular location
        if [[ $use_clone_from_backup -eq 1 ]]; then
            local regular_target
            regular_target="$(git-sync --show-backup-cache | sed 's|^backup/||' | fzf --tac --exact --no-sort)"
            if [[ -z "$regular_target" ]]; then
                return 130
            fi

            local backup_target="backup/$regular_target"

            # Get the backup repo directory to extract origin URL
            local backup_repo_dir
            backup_repo_dir="$(git-sync "$backup_target")"
            if [[ -z "$backup_repo_dir" || ! -d "$backup_repo_dir" ]]; then
                echo "error: backup repository not found: $backup_target" >&2
                return 1
            fi

            # Get origin URL from backup repo
            local origin_url
            origin_url="$(git -C "$backup_repo_dir" remote get-url origin 2>/dev/null)"
            if [[ -z "$origin_url" ]]; then
                echo "error: no origin found in backup repository" >&2
                return 1
            fi

            # Clone to regular location
            local repo_dir
            repo_dir="$(git-sync "$regular_target")"
            if [[ -n "$repo_dir" ]]; then
                print -s -- gs --clone-from-backup
                cd "$repo_dir"
            fi
            return $?
        fi

        # If first arg is a flag (for git-sync), pass through
        case "${args[1]}" in
            -*)
                git-sync "${args[@]}"
                return $?
                ;;
        esac

        case ${#args[@]} in
            0)
                if [[ $use_backup -eq 1 ]]; then
                    target="$(git-sync --show-backup-cache | sed 's|^backup/||' | fzf --tac --exact --no-sort)"
                    if [ -z "$target" ]; then
                        return 130
                    fi
                    target="backup/$target"
                elif [[ $only_remote -eq 1 ]]; then
                    target="$(git-sync --show-remote-cache | fzf --tac --exact --no-sort)"
                    if [ -z "$target" ]; then
                        return 130
                    fi
                    target="backup/$target"
                else
                    target="$(git-sync --show-cache --remote | fzf --tac --exact --no-sort)"
                    if [ -z "$target" ]; then
                        return 130
                    fi
                fi
                ;;
            1)
                target="${args[1]}"
                if [[ $use_backup -eq 1 && "$target" != backup/* ]]; then
                    target="backup/$target"
                fi
                ;;
            *)
                echo 'error: unexpected arguments' >&2
                return 1
        esac

        if ! [ -t 1 ]; then
            git-sync --show-dir "$target"
            return
        fi

        local repo_dir
        if [[ $use_backup -eq 1 ]]; then
            print -s -- gs --backup "$target"
        else
            print -s -- gs "$target"
        fi
        repo_dir="$(git-sync "$target")"
        if [ -z "$repo_dir" ]; then
            return 130
        else
            cd "$repo_dir"
        fi
    }
fi
