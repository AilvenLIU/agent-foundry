---
name: python-env
description: Diagnose and repair pyenv and Poetry problems, such as the wrong interpreter, a venv outside the project, a pyenv build missing stdlib extensions, a leaked VIRTUAL_ENV, or Poetry not found. Use when poetry install, poetry run or interpreter selection fails.
---

# Python environment recovery

Target state: pyenv selects Python 3.10+ for the project (`pyenv local <version>`), Poetry
comes from pipx, and `poetry.toml` has `virtualenvs.in-project = true` so the venv is `.venv/`.

Check first:

```bash
poetry --version; poetry env info; pyenv version; echo "${VIRTUAL_ENV:-unset}"; cat poetry.toml
```

## Common faults

- **Leaked `VIRTUAL_ENV` in the login shell.** Unset it and remove whatever exports it
  from the shell profile. `poetry run` setting it for child processes is normal.
- **Venv outside the project.** Create `poetry.toml` with the in-project setting, then
  `poetry env remove --all && poetry env use "$(pyenv which python)" && poetry install`.
- **pyenv not initialised.** Run `~/.pyenv/bin/pyenv init --install`, then `exec zsh -l`.
- **Incomplete interpreter.** `pyenv install` can succeed while warning about `_bz2`,
  `_curses`, `_ctypes`, `readline`, `_sqlite3` or `_lzma`. That interpreter is unusable.
  Install the OS build prerequisites (on Debian/Ubuntu: `build-essential libssl-dev
  zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libncurses-dev xz-utils tk-dev
  libffi-dev liblzma-dev libgdbm-dev libnss3-dev uuid-dev`; ask before using sudo),
  `pyenv uninstall -f <version>`, reinstall, then rebuild the Poetry env as above and
  check `poetry run python -c 'import bz2, curses, ctypes, lzma, readline, sqlite3'`.
- **Poetry missing.** `pipx install poetry`. Do not use the curl installer or brew.

Never fall back to system Python or pip. Uninstalling an interpreter is destructive:
name the exact version and confirm with the user first.
