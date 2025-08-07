if [[ $OSTYPE == darwin* ]]; then
    # ugh - Apple overrides PATH in /etc/zprofile
    # disable that bullshit and update PATH here
    # (normally runs: eval `/usr/libexec/path_helper -s`)
    setopt no_global_rcs
    path=(
        "$path[@]"
        /Library/Apple/usr/bin
    )

    export LANG=en_US.UTF-8
    export HOMEBREW_NO_ANALYTICS=1

    path=(
        "$DOTFILES/scripts/macos"
        /opt/homebrew/bin
        /opt/homebrew/opt/coreutils/libexec/gnubin
        /opt/homebrew/opt/gnu-sed/libexec/gnubin
        /opt/homebrew/opt/gnu-tar/libexec/gnubin
        /opt/homebrew/opt/curl/bin
        "$path[@]"
    )

    manpath=(
        /opt/homebrew/opt/*/libexec/gnuman
        /usr/share/man
        "$manpath[@]"
    )

    fpath=(
        /opt/homebrew/share/zsh/site-functions
        "$fpath[@]"
    )
fi
