if command -q minikube
    function minikube_env
        minikube docker-env --shell fish | source
        set -l test_host (string replace -r ':[^:]*$' '' -- $DOCKER_HOST)
        set test_host (string replace -r '.*/' '' -- $test_host)
        set -gx TEST_HOST $test_host
    end
end
