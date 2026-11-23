if test -d ~/.local/share/pyenv
    set -gx PYENV_ROOT ~/.local/share/pyenv
    fish_add_path -Pm \
        $PYENV_ROOT/plugins/pyenv-global-links \
        $PYENV_ROOT/bin \
        $PYENV_ROOT/shims
else
    set -e PYENV_ROOT
end
