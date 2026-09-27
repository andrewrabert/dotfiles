import os
import socket


def name():
    return os.environ.get("HOST_DOTFILES") or socket.gethostname()
