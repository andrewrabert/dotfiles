#!/usr/bin/env python3
"""Generate a fake SRT track for a media file.

Subtitle visible for 4s, hidden for 2s, repeating until the file ends.
"""

import argparse
import asyncio
import asyncio.subprocess
import pathlib
import sys

DEFAULT_SHOW_SECONDS = 5
DEFAULT_HIDE_SECONDS = 0


class UserError(Exception):
    pass


class ffprobe:
    @staticmethod
    async def duration(path):
        proc = await asyncio.create_subprocess_exec(
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            "--",
            str(path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise UserError(f"ffprobe failed: {stderr.decode().strip()}")
        return float(stdout.decode().strip())


def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(text, duration, show_duration, hide_duration):
    cycle_seconds = show_duration + hide_duration
    total = int((duration - show_duration) // cycle_seconds) + 1
    if total < 1:
        return ""
    width = len(str(total))
    lines = []
    for n in range(1, total + 1):
        start = (n - 1) * cycle_seconds
        end = start + show_duration
        lines.append(str(n))
        lines.append(f"{format_timestamp(start)} --> {format_timestamp(end)}")
        lines.append(f"{text} - {n:0{width}d}")
        lines.append("")
    return "\n".join(lines)


async def main():
    parser = argparse.ArgumentParser(
        description="Generate a fake SRT subtitle file from a media file's duration."
    )
    parser.add_argument("--text", required=True, help="subtitle text prefix")
    parser.add_argument(
        "--show",
        metavar="SECONDS",
        type=float,
        default=DEFAULT_SHOW_SECONDS,
        help="how long each text is shown (default: %(default)s)",
    )
    parser.add_argument(
        "--hide",
        metavar="SECONDS",
        type=float,
        default=DEFAULT_HIDE_SECONDS,
        help="how long between each text (default: %(default)s)",
    )
    parser.add_argument(
        "file", type=pathlib.Path, help="input video or audio file"
    )
    args = parser.parse_args()

    if not args.file.exists():
        raise UserError(f"file not found: {args.file}")

    duration = await ffprobe.duration(args.file)
    print(
        generate_srt(
            args.text,
            duration,
            show_duration=args.show,
            hide_duration=args.hide,
        )
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except UserError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
