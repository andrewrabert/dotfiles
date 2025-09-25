typeset -U path
typeset -U manpath

zmodload zsh/stat
export DOTFILES=${$(zstat +link ~/.zshrc)%%/zsh/.zshrc}
export EDITOR=nvim
export LESSHISTFILE=/dev/null
export OPENER=open

if [ -e ~/.zshenv.local ]; then
    . ~/.zshenv.local
fi

for plugin in "$DOTFILES"/zsh/plugins/*/.zshenv(N); do
    . "$plugin"
done

path=(
    "${DOTFILES}/.bin"
    "$path[@]"
)

zshenv_host="$DOTFILES/zsh/hosts/$HOST/.zshenv"
if [[ -r "$zshenv_host" ]]; then
    . "$zshenv_host"
fi
unset zshenv_host

path=(
    ~/.local/bin
    "$path[@]"
)
