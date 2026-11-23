if test -d ~/.local/share/nvm
    set -gx NVM_DIR ~/.local/share/nvm
    fish_add_path -Pm $NVM_DIR/current/bin
else
    set -e NVM_DIR
end
