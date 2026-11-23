if set -q NVM_DIR; and test -d $NVM_DIR
    # nvm is a bash function, so it runs in bash. Environment changes it
    # makes (e.g. `nvm use`) do not carry back into fish; PATH uses the
    # $NVM_DIR/current symlink instead.
    function nvm
        bash -c '. "$NVM_DIR/nvm.sh" && nvm "$@"' nvm $argv
    end
end
