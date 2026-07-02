#!/usr/bin/env python3
import json
import pathlib
import sys

DATA = json.load(sys.stdin)

PROJECT_DIR = pathlib.Path(DATA["workspace"]["project_dir"]).absolute()
CWD = pathlib.Path(DATA["cwd"]).absolute()
SESSION_ID = DATA["session_id"]
TRANSCRIPT = pathlib.Path(DATA["transcript_path"]).absolute()

HOME = pathlib.Path.home().absolute()

SESSION_SHORT = 6


def grey(text):
    GREY = "\033[90m"
    RESET = "\033[0m"
    return GREY + text + RESET


def link(target, text):
    return f"\033]8;;file://{target}\033\\{text}\033]8;;\033\\"


if PROJECT_DIR == HOME:
    project = "~"
elif PROJECT_DIR.is_relative_to(HOME):
    project = f"~/{PROJECT_DIR.relative_to(HOME)}"
else:
    project = str(PROJECT_DIR)

cwd = f"{CWD.relative_to(PROJECT_DIR)}/" if CWD != PROJECT_DIR else ""
path = link(CWD, f"{project}/{grey(cwd)}")
session = link(TRANSCRIPT, grey(SESSION_ID[:SESSION_SHORT]))
print(f"{session} {path}")
