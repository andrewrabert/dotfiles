import json
import shutil

from dotfiles import xdg


def main():
    if not shutil.which("discord"):
        return
    path = xdg.config_home() / "discord" / "settings.json"
    if not path.exists():
        return
    settings = json.loads(path.read_text())
    if not settings.get("SKIP_HOST_UPDATE"):
        settings["SKIP_HOST_UPDATE"] = True
        path.write_text(json.dumps(settings))
