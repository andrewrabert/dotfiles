test -r ~/.dotfiles/private/fish/env.fish; and source ~/.dotfiles/private/fish/env.fish
set -gx LIBVIRT_DEFAULT_URI qemu:///system
set -gx CLAUDE_CONFIG_DIR ~/.local/share/claude-code/default
set -gx NOTES_DIR ~/syncthing/default/notes
set -gx JEVREV_ENV_FILE "$DOTFILES_PRIVATE/jevrev.env"
