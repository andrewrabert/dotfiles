if command -q go
    set -gx GOPATH ~/.local/share/go
    fish_add_path -Pm $GOPATH/bin
end
