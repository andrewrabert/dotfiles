for f in ~/.dotfiles/aweber/fish/env.fish ~/.dotfiles/private/fish/env.fish
    test -r $f; and source $f
end
