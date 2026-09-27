import pydantic

from dotfiles import fs


class InstalledCache:
    def __init__(self, path, model):
        self._path = path
        self._model = model

    def load(self, binary):
        try:
            installed = self._model.model_validate_json(self._path.read_text())
            digest = fs.sha256(binary)
        except FileNotFoundError, pydantic.ValidationError:
            return None
        if installed.sha256 != digest:
            print("Installed binary does not match recorded hash")
            return None
        return installed

    def write(self, installed):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(installed.model_dump_json(indent=2) + "\n")
