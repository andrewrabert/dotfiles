set -gx PYTHONUSERBASE ~/.local/share/pythonuser

if test -d $PYTHONUSERBASE
    fish_add_path -Pm $PYTHONUSERBASE/bin
    # https://github.com/python-poetry/poetry/issues/1917#issuecomment-1235998997
    set -gx PYTHON_KEYRING_BACKEND keyring.backends.null.Keyring
else if not command -q python
    set -e PYTHONUSERBASE
end
