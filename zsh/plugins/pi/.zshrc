if command -v pi > /dev/null; then
    pi() {
        PI_SKIP_VERSION_CHECK=1 command pi "$@"
    }
fi
