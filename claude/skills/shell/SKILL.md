---
name: shell
description: Use when writing shell scripts - POSIX sh default, 4-space indent, set -eu, uppercase constants, printf over echo, explicit error handling (user)
---

# Shell Script Preferences

**Project conventions take precedence unless user says otherwise.**

## Shebang

**POSIX sh (default):**

```sh
#!/usr/bin/env sh
```

**Only use bash/zsh when their specific features are needed.**

## Error Handling

Always set error flags at script start:

```sh
set -eu
```

- `-e`: exit on first error
- `-u`: error on undefined variables
- Add `-x` for debugging when needed

**Trap for cleanup:**

```sh
trap 'cleanup' EXIT
trap 'cleanup; exit 1' INT TERM
```

**Error messages to stderr:**

```sh
echo 'error: cannot find config' >&2
exit 1
```

## Variable Naming

| Context | Style | Example |
|---------|-------|---------|
| Constants/exports | UPPER_SNAKE | `YELLOW`, `GIT_DIR`, `NO_PUSH` |
| Local variables | lower_snake | `script_name`, `target`, `was_readonly` |

## Variable Expansion

**Always use braces:** `${VAR}` not `$VAR`

**Exception:** Special parameters use bare form: `$#`, `$@`, `$?`, `$0`, `$1`, `$2`, etc.

```sh
# Correct
echo "${HOME}"
printf '%s\n' "${message}"
[ $# -gt 0 ]
main "$@"

# Wrong
echo $HOME
printf '%s\n' "$message"
[ ${#} -gt 0 ]
main "${@}"
```

## Quoting

- **Double quotes** for variable expansion: `"${VAR}"`
- **Single quotes** for literals: `'literal string'`
- **Always quote** `"$@"` and path variables

## Functions

```sh
function_name() {
    # body
}
```

- No `function` keyword (POSIX compatibility)
- Opening brace on same line
- 4-space indent

## Indentation

**4 spaces.** No tabs.

## Output

**Colors:**

```sh
YELLOW='\033[1;33m'
RESET='\033[0m'

log() {
    printf '%b%s%b\n' "${YELLOW}" "$1" "${RESET}"
}
```

## Argument Parsing

```sh
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        --force)
            FORCE=1
            shift
            ;;
        *)
            echo "error: unknown option '$1'" >&2
            exit 1
            ;;
    esac
done
```

## Help Text

```sh
show_help() {
    cat << EOF
Usage: $(basename "$0") [options]

Options:
    -h, --help    Show this help
    --force       Force operation
EOF
}
```

## Command Checking

```sh
if ! command -v program > /dev/null; then
    echo 'error: program not found' >&2
    exit 1
fi
```

## Script Structure

1. Shebang
2. `set` directives
3. Constants (UPPERCASE)
4. Color definitions (if used)
5. Helper functions
6. Main logic / argument parsing
7. Execution

**Example:**

```sh
#!/usr/bin/env sh
set -eu

YELLOW='\033[1;33m'
RESET='\033[0m'

log() {
    printf '%b%s%b\n' "${YELLOW}" "$1" "${RESET}"
}

show_help() {
    cat << EOF
Usage: $(basename "$0") [options]
EOF
}

main() {
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                shift
                ;;
        esac
    done

    log "Starting..."
}

main "$@"
```

## Parameter Expansion

```sh
${VAR:-default}     # default if unset/empty
${VAR##*/}          # basename-like
${VAR%.*}           # remove extension
```

## Temporary Files

```sh
temp_file="$(mktemp)"
trap 'rm -f "${temp_file}"' EXIT
```

## Common Mistakes

- Using `$VAR` instead of `${VAR}` (except special params: `$#`, `$@`, `$1`, etc.)
- Unquoted variables: `${VAR}` instead of `"${VAR}"`
- Using bashisms in POSIX scripts (arrays, `[[`, `source`)
- Missing `set -eu` at start
- Error messages not going to stderr
- Using `function` keyword
- Tab indentation instead of 4 spaces
