# Directives
- Prefer simplicity.
- Prefer readability.
- Never over-complicate things.
- Never add unnecessary comments.

# Shell Tools
- You run in an environment where `ast-grep` is available; whenever a search requires syntax-aware or structural matching, default to `ast-grep --lang <language> -p '<pattern>'` and avoid falling back to text-only tools like `rg` or `grep` unless I explicitly request a plain-text search.
- Prefer `fd` over `find`
- Prefer `rg` over `grep`

# Important Instructions
- Do what has been asked; nothing more, nothing less.
- NEVER create files unless they're absolutely necessary for achieving your goal.
- ALWAYS prefer editing an existing file to creating a new one.
- NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the user.
