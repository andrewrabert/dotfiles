#!/usr/bin/env python3
import argparse
import pathlib
import subprocess


def fzf(data, header=None, query=None):
    args = [
        "fzf",
        "--black",
        "--prompt=",
        "--no-info",
        "--exact",
        "--no-sort",
        "--no-extended",
        "-i",
        "--layout=reverse",
        "--print-query",
    ]
    if header is not None:
        data = [header, *data]
        args.append("--header-lines=1")
    if query is not None:
        args.append(f"--query={query}")
    proc = subprocess.run(
        args,
        input="\n".join(data).encode(),
        stdout=subprocess.PIPE,
    )
    try:
        result = proc.stdout.decode().splitlines()[-1]
    except IndexError:
        result = None

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--titles", type=pathlib.Path)
    parser.add_argument("path", type=pathlib.Path)
    args = parser.parse_args()

    titles = args.titles.read_text().splitlines()
    for path in args.path.iterdir():
        if path.is_dir():
            raise NotImplementedError
        if path.is_file() and path.suffix == ".mkv":
            result = fzf(titles, header=path.name, query=path.name.split()[0])
            if result is not None:
                newpath = path.with_name(result + ".mkv")
                if path == newpath:
                    continue
                if newpath.exists():
                    raise RuntimeError
                print(newpath)
                path.replace(newpath)


if __name__ == "__main__":
    main()
