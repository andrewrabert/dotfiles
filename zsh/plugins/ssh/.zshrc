# Limit ssh completions to hosts only
zstyle ':completion:*:ssh:argument-1:*' tag-order hosts

# hosts before files (not the default)
zstyle ':completion:*:scp:*' tag-order hosts files
