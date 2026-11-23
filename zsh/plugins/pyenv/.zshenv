export PYENV_ROOT=~/.local/share/pyenv

if [ -d "$PYENV_ROOT" ]; then
    path=(
        "${PYENV_ROOT}/plugins/pyenv-global-links"
        "${PYENV_ROOT}/bin"
        "${PYENV_ROOT}/shims"
        "$path[@]"
    )
else
    unset PYENV_ROOT
fi
