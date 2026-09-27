import pathlib

STIGNORE_INCLUDE = {
    "syncthing/default": ".syncthing/ignore_default_folder.txt",
    "storage/shared": "syncthing/default/.syncthing/ignore_android.txt",
}


def main():
    for sync_folder, include_path in STIGNORE_INCLUDE.items():
        sync_folder = pathlib.Path.home() / sync_folder
        expected_contents = f"#include {include_path}\n"

        needs_write = False
        stignore = sync_folder / ".stignore"
        if (sync_folder / ".stfolder").is_dir():
            if stignore.is_file():
                if stignore.read_text() != expected_contents:
                    needs_write = True
            else:
                needs_write = True

        if needs_write:
            print("Writing", stignore)
            stignore.write_text(expected_contents)
