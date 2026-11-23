if [ -d "$NVM_DIR" ]; then
    # nvm.sh nearly triples shell startup time, lazy load it!
    nvm() {
        . "$NVM_DIR/nvm.sh" && nvm "$@"
    }
fi
