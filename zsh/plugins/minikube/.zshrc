if command -v minikube > /dev/null; then
    minikube_env() {
        eval "$(minikube docker-env)"
        local test_host="${DOCKER_HOST%:*}"
        test_host="${test_host##*/}"
        export TEST_HOST="$test_host"
    }
fi
