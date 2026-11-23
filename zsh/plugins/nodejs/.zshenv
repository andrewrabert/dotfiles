export NVM_DIR=~/.local/share/nvm

if [ -d "$NVM_DIR" ]; then
    path=(
        "${NVM_DIR}/current/bin"
        "$path[@]"
    )
else
    unset NVM_DIR
fi
