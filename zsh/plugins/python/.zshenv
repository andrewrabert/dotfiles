export PYTHONUSERBASE=~/.local/share/pythonuser

if [ -d "$PYTHONUSERBASE" ]; then
    path=(
        "${PYTHONUSERBASE}/bin"
        "$path[@]"
    )
    # https://github.com/python-poetry/poetry/issues/1917#issuecomment-1235998997
    export PYTHON_KEYRING_BACKEND='keyring.backends.null.Keyring'

elif ! command -v python > /dev/null; then
    unset PYTHONUSERBASE
fi
