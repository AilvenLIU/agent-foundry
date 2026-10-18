## Python

- Poetry owns the environment and dependencies. Python 3.10+ via pyenv; Poetry from
  pipx at `~/.local/bin/poetry` (not the curl installer or brew); `poetry.toml` sets
  `virtualenvs.in-project = true`.
- Never run `pip`, `python -m pip`, bare `python`, or a hand-made venv. Use
  `poetry add [--group dev] <pkg>` and `poetry run python|pytest|ruff|mypy`.
  Commit `poetry.lock` together with `pyproject.toml`.
- A custom package source must be HTTPS, carry no credentials in files, and set an
  explicit priority. Changing an index is a supply-chain decision: ask first.
- Layout: `src/<package>/` and `tests/`.
- Tools: `ruff format` and `ruff check` (line length 100), pytest. Type-hint public
  functions; run mypy only if the project configures it.
- No bare `except:`, no mutable default arguments. Catch specific exceptions and do
  not swallow them. Docstrings only where the signature does not explain itself.
- Interpreter or Poetry trouble: use the `python-env` skill.
