#!/usr/bin/env python3
import json
import pathlib
import sys

DATA = json.load(sys.stdin)

WORKSPACE_PROJECT_DIR = pathlib.Path(
    DATA["workspace"]["project_dir"]
).absolute()
CWD = pathlib.Path(DATA["cwd"]).absolute()
SESSION_ID = DATA["session_id"]

HOME = pathlib.Path.home().absolute()


def grey(text):
    GREY = "\033[90m"
    RESET = "\033[0m"
    return GREY + text + RESET


if WORKSPACE_PROJECT_DIR.is_relative_to(HOME):
    project = f"~/{WORKSPACE_PROJECT_DIR.relative_to(HOME)}/"
else:
    project = f"{WORKSPACE_PROJECT_DIR}/"

cwd = f"{CWD.relative_to(WORKSPACE_PROJECT_DIR)}/" if CWD != WORKSPACE_PROJECT_DIR else ""
print(f"{grey(SESSION_ID[:8])} {project}{grey(cwd)}")
