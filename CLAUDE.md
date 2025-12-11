# Dotfiles Repository

Personal configuration files. Cross-platform (Arch Linux, macOS, other Linux). Desktop uses Arch + KDE Plasma.

## Structure

**App Configs:** nvim/, zsh/, kde/, tmux/, yazi/, mpv/, foot/, pandoc/, etc.

**System:** systemd/user/, pipewire/, networkmanager/, pacman/, fontconfig/

**Dev Tools:** rust-tools/, python/, ruff/, qmk_firmware/

**Scripts:** scripts/ with subdirs:
- commands/ - per-tool wrappers (42 subdirs)
- terminal/ - text/archive/image utilities
- media/ - audio/video processing
- hosts/ - host-specific scripts
- archlinux/, aws/, email/, provision/

**Update System:** full-update/ - numbered scripts (00-99) for ordered updates

**Host Configs:** non-user/ - per-machine configs (mars, sol, phobos, retro-*, lounge-htpc)

**.bin/** - 200+ symlinks to scripts for PATH access

## Patterns

- Modular by tool/domain
- Host-aware (zsh/hosts/, systemd/user/, non-user/)
- Ordered update pipeline via numbered scripts
- Arch Linux primary, with termux/dosbox support
