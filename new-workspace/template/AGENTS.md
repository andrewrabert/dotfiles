# ${name}

Local research/work workspace. No remote.

- Research goes in `docs/research/`, plans in `docs/plans/`, decisions in `docs/adr/`,
  scratch in `docs/notes/`.
- Clone reference repos into `external/` (git-ignored) — don't edit them expecting
  commits in this repo.
- Read `CONTEXT.md` for the shared terminology before writing.

## Tasks

`just` runs the project tasks (recipes load `.env` if present):

```
$ just --list
Available recipes:
    run *args        # Run a command with .env loaded

    [git]
    clone url dir="" # Clone a repo into external/ (pass dir to rename if the name is taken)
```
