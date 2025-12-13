#!/usr/bin/env python3
import argparse
import json
import pathlib
import sys

OVERRIDES = {
    "PS": "PSX",
}


def get_suffixes(sdcard_dir, emu_name):
    if emu_name in OVERRIDES:
        emu_name = OVERRIDES[emu_name]
    path = sdcard_dir / "Emu" / emu_name / "config.json"
    data = json.loads(path.read_text())
    return [
        "." + ext
        for ext in data["extlist"].split("|")
        if ext not in ("miyoocmd")
    ]


SKIP = [
    "DOS",
    "PORTS",
    "PICO",
]


def find_missing(sdcard_dir, rom_path, suffixes):
    img_path = rom_path / "Imgs"
    found_missing = False
    if rom_path.name == "PS":
        for path in rom_path.iterdir():
            if not path.is_dir():
                continue
            if path.name == "Imgs":
                continue
            name = path.name.removeprefix(".")
            img = img_path / f"{name}.png"
            if not img.exists():
                found_missing = True
                print(path.relative_to(sdcard_dir))
    else:
        for path in rom_path.iterdir():
            if not path.is_file():
                continue
            if path.suffix == ".miyoocmd":
                continue
            if path.suffix.lower() not in suffixes:
                continue
            img = img_path / f"{path.stem}.png"
            if not img.exists():
                found_missing = True
                print(path.relative_to(sdcard_dir))
    return found_missing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sdcard_dir", type=pathlib.Path)
    args = parser.parse_args()

    found_missing = False
    for path in (args.sdcard_dir / "Roms").iterdir():
        if not path.is_dir():
            continue
        emu_name = path.name
        if emu_name in SKIP:
            continue
        try:
            suffixes = get_suffixes(args.sdcard_dir, emu_name)
        except FileNotFoundError:
            continue
        if find_missing(args.sdcard_dir, path, suffixes):
            found_missing = True
    if found_missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
