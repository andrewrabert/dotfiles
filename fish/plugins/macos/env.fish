# a file only macOS has, so no external command runs at startup
if test -e /System/Library/CoreServices/SystemVersion.plist
    # zsh needed no_global_rcs to stop /etc/zprofile running path_helper.
    # fish applies /etc/paths itself before this file, so the prepends
    # below still win.
    fish_add_path -Pa /Library/Apple/usr/bin /usr/local/bin

    set -gx LANG en_US.UTF-8
    set -gx HOMEBREW_NO_ANALYTICS 1

    fish_add_path -Pm \
        $DOTFILES/scripts/macos \
        /opt/homebrew/bin \
        /opt/homebrew/opt/coreutils/libexec/gnubin \
        /opt/homebrew/opt/gnu-sed/libexec/gnubin \
        /opt/homebrew/opt/gnu-tar/libexec/gnubin \
        /opt/homebrew/opt/curl/bin

    set -l manpath /opt/homebrew/opt/*/libexec/gnuman /usr/share/man
    for p in $MANPATH
        contains -- $p $manpath; or set -a manpath $p
    end
    set -gx --path MANPATH $manpath

    # Homebrew's fish already includes /opt/homebrew/share/fish/vendor_completions.d
end
