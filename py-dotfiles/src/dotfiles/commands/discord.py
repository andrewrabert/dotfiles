import json
import pathlib
import shutil


def main():
    if not shutil.which("discord"):
        return
    path = pathlib.Path("~/.config/discord/settings.json").expanduser()
    if not path.exists():
        return
    settings = json.loads(path.read_text())
    if not settings.get("SKIP_HOST_UPDATE"):
        settings["SKIP_HOST_UPDATE"] = True
        path.write_text(json.dumps(settings))
