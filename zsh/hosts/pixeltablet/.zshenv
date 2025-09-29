. ~/.dotfiles/private/zsh/.zshenv || true

# fix building python pillow
export INCLUDE="$PREFIX/include" 
export LDFLAGS=" -lm"
