if set -q BASE16_SHELL
    if test -z "$SSH_CONNECTION"; and test -z "$TMUX"; and test -f ~/.base16_theme
        # The theme is a sh script that writes terminal escapes, so run it
        # rather than source it. Variables it exports do not reach fish.
        sh ~/.base16_theme
    end
end
