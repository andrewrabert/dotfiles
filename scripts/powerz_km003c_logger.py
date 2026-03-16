#!/usr/bin/env python3
import argparse
import datetime
import json
import pathlib
import time


class Style:
    FG_BLACK = "\u001b[30m"
    FG_RED = "\u001b[31m"
    FG_GREEN = "\u001b[32m"
    FG_YELLOW = "\u001b[33m"
    FG_BLUE = "\u001b[34m"
    FG_MAGENTA = "\u001b[35m"
    FG_CYAN = "\u001b[36m"
    FG_WHITE = "\u001b[37m"

    BG_BLACK = "\u001b[40m"
    BG_RED = "\u001b[41m"
    BG_GREEN = "\u001b[42m"
    BG_YELLOW = "\u001b[43m"
    BG_BLUE = "\u001b[44m"
    BG_MAGENTA = "\u001b[45m"
    BG_CYAN = "\u001b[46m"
    BG_WHITE = "\u001b[47m"

    RESET = "\u001b[0m"
    BRIGHT = "\u001b[1m"
    DIM = "\u001b[2m"
    ITALIC = "\u001b[3m"
    REVERSE = "\u001b[7m"
    UNDERLINE = "\u001b[4m"

    @classmethod
    def strip(cls, text):
        for key, value in cls.__dict__.items():
            if isinstance(value, str):
                text = text.replace(value, "")
        return text


def find_device():
    matches = []
    for path in pathlib.Path("/sys/bus/usb/drivers/powerz").iterdir():
        if not path.is_dir():
            continue
        hwmon = path / "hwmon"
        if not hwmon.exists():
            continue
        hwmon_num = list(hwmon.iterdir())
        if len(hwmon_num) != 1:
            raise RuntimeError
        matches.append(hwmon_num[0])
    match len(matches):
        case 1:
            return matches[0]
        case 0:
            raise RuntimeError("device not found")
        case _:
            raise RuntimeError("multiple devices found")


def read_device(hwmon_path):
    state_raw = {}
    state = {}
    for path in hwmon_path.iterdir():
        if not path.is_file():
            continue
        if not path.name.endswith(("_average", "_input", "_label")):
            continue
        key, key_type = path.name.split("_")
        state_raw.setdefault(key, {})
        lines = path.read_text().splitlines()
        if len(lines) != 1:
            raise RuntimeError
        value = lines[0]
        match key_type:
            case "label":
                pass
            case "input":
                value = int(value)
            case "average":
                continue
            case _:
                raise RuntimeError("unexpected")
        state_raw[key][key_type] = value
    for v in state_raw.values():
        label = v["label"]
        value = v["input"]
        if label in state:
            raise RuntimeError
        state[label] = value
    return state


def format_human(now, state):
    new_state = {}
    ibus = None
    vbus = None
    for key, value in state.items():
        match key:
            case "IBUS":
                key = "IBUS (A)"
                if value < 0:
                    value = -1 * value
                value = value * 0.001
                ibus = value
                value = f"{value:.3f}"
            case "VBUS":
                key = "VBUS (V)"
                value = value * 0.001
                vbus = value
                value = f"{value:.3f}"
            case _:
                continue
        new_state[key] = value
    state = new_state
    state["PWR (W)"] = f"{ibus * vbus:.3f}"
    line = [now.astimezone(tz=None).strftime("%Y-%m-%d %H:%M:%S")]
    for key in ("VBUS (V)", "IBUS (A)", "PWR (W)"):
        match key:
            case "VBUS (V)":
                color = Style.FG_GREEN
            case "IBUS (A)":
                color = Style.FG_RED
            case "PWR (W)":
                color = Style.FG_BLUE
        value = new_state[key]
        line.append(f"{Style.BRIGHT}{color}{key}:{Style.RESET} {value}")
    line = "   ".join(line)
    return line


def format_raw(ts, state):
    data = {
        "timestamp": ts.isoformat(),
        "state": state,
    }
    line = json.dumps(data, separators=(",", ":"), sort_keys=True)
    return line


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--interval", type=int, default=1)
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        help="write raw values as JSON to a file",
    )
    parser.add_argument("-i", "--input", type=pathlib.Path)
    args = parser.parse_args()

    if args.input:
        for raw_line in args.input.read_text().splitlines():
            data = json.loads(raw_line)
            line = format_human(
                now=datetime.datetime.fromisoformat(data["timestamp"]),
                state=data["state"],
            )
            print(line)
        parser.exit()

    path = find_device()
    handle = None
    if args.output:
        handle = open(args.output, "w")
    while True:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        state = read_device(path)
        print(format_human(now, state))
        if handle:
            handle.write(format_raw(now, state) + "\n")
            handle.flush()
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
