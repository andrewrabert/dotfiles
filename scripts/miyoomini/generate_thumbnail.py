#!/usr/bin/env python3
import argparse
import asyncio
import pathlib
import tempfile


class ProcessError(Exception):
    def __init__(self, process, message=None):
        self.process = process
        self.message = message

    def __str__(self):
        proc = self.process

        text = f'exit {proc.returncode}'
        if self.message is not None:
            text = f'{text} - {self.message}'

        try:
            args = proc._transport._extra['subprocess'].args
        except (AttributeError, KeyError):
            pass
        else:
            text = f'{text}: {args}'
        return text


def safe_write(path, data):
    path = pathlib.Path(path)
    if isinstance(data, str):
        data = data.encode()
    with tempfile.NamedTemporaryFile(delete=False, dir=path.parent) as handle:
        temp_path = pathlib.Path(handle.name)
        try:
            temp_path.write_bytes(data)
            temp_path.rename(path)
        finally:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


async def imgoptim(*path, fast=False, quiet=False, strip=False):
    args = ['imgoptim']
    if fast:
        args.append('--fast')
    if quiet:
        args.append('--quiet')
    if strip:
        args.append('--strip')
    args.extend(['--', *path])
    proc = await asyncio.create_subprocess_exec(*args)
    await proc.communicate()
    if proc.returncode:
        raise ProcessError(proc)


async def resize_to_miyoo_thumbnail(source, target, pico8=False):
    resolution = '250x360'

    args = [
        'magick', source,
    ]
    if pico8:
        args.extend(['-crop', '128x128+16+24'])

    args.extend([
        '-scale', resolution,
        '-background', 'transparent',
        '-gravity', 'center',
        '-extent', resolution,
        target,
    ])
    proc = await asyncio.create_subprocess_exec(*args)
    await proc.communicate()
    if proc.returncode:
        raise ProcessError(proc)


SUFFIX = '.png'


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=pathlib.Path)
    parser.add_argument('--fast', action='store_true')
    parser.add_argument('--pico8', action='store_true')
    parser.add_argument('path', type=pathlib.Path)
    args = parser.parse_args()

    if args.output is None:
        output = args.path
        if args.path.suffix != SUFFIX:
            output = output.with_suffix(SUFFIX)
    else:
        output = args.output
        if args.path.suffix != SUFFIX:
            raise argparse.ArgumentError(f'suffix must be {SUFFIX}')

    with tempfile.NamedTemporaryFile(suffix=SUFFIX) as tmp:
        tmp = pathlib.Path(tmp.name)
        await resize_to_miyoo_thumbnail(args.path, tmp, pico8=args.pico8)
        await imgoptim(tmp, fast=args.fast, quiet=True, strip=True)
        safe_write(output, tmp.read_bytes())


if __name__ == '__main__':
    asyncio.run(main())
