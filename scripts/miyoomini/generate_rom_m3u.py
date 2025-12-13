#!/usr/bin/env python3
import argparse
import pathlib


def generate_m3u(root):
    for path in root.iterdir():
        if not path.is_dir():
            continue
        child_cue = []
        for child in path.iterdir():
            if child.suffix.lower() == ".cue":
                child_cue.append(child.relative_to(root))
        if not child_cue:
            continue
        expected = "\n".join(str(p) for p in sorted(child_cue))
        m3u_path = root / f"{path.name.removeprefix('.')}.m3u"
        if m3u_path.exists() and m3u_path.read_text() == expected:
            continue
        print("Writing", m3u_path)
        m3u_path.write_text(expected)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sdcard_dir", type=pathlib.Path)
    args = parser.parse_args()

    generate_m3u(args.sdcard_dir / "Roms" / "PS")


if __name__ == "__main__":
    main()
