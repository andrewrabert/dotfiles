test -r ~/.dotfiles/private/fish/env.fish; and source ~/.dotfiles/private/fish/env.fish

# fix building python pillow
set -gx INCLUDE "$PREFIX/include"
set -gx LDFLAGS ' -lm'
