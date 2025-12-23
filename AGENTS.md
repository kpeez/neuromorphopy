# Repository Guidelines

## Project Structure & Module Organization

`neuromorphopy/` contains the Python package. Core modules live at the top level (`api.py`, `cli.py`, `query.py`), with helpers in `neuromorphopy/utils/` and file I/O in `neuromorphopy/io/`. Documentation is in `docs/` and configured by `mkdocs.yaml`. Example notebooks live in `notebooks/`. Build artifacts may appear in `dist/` and should not be edited by hand.

## Build, Test, and Development Commands

Use `uv` for environment and tooling.

```bash
just               # list available tasks
just install       # uv sync + pre-commit install
just check         # ruff check + pre-commit
uv run ty check    # type checking
just test          # pytest
just docs          # mkdocs dev server
just docs-test     # mkdocs build --strict
```

If `just` is unavailable, run the underlying `uv run …` commands directly.

## Coding Style & Naming Conventions

Python 3.11+ with 4‑space indentation. Use `lower_snake_case` for modules, functions, and variables. Keep names descriptive (e.g., `query_filters`, `download_neurons`). Formatting and linting are enforced by Ruff (`line-length = 100`, double quotes). Prefer small, focused modules under `neuromorphopy/`; keep CLI logic in `cli.py` and API behavior in `api.py`.

## Testing Guidelines

Pytest is configured in `pyproject.toml` with `tests/` as the root. Add new tests under `tests/` using `test_*.py` naming. Run tests with:

```bash
uv run pytest
```

## Commit & Pull Request Guidelines

Commit messages in history are short, imperative, and mostly lowercase (e.g., “update config”, “bump version”, “add logo”). Include issue/PR numbers when applicable (e.g., `(#18)`). For PRs, include a concise summary, note any user‑facing CLI changes, and update docs when behavior or flags change. If tests aren’t added, explain why in the PR description.

## Security & Configuration Tips

Do not commit secrets. Prefer environment variables for credentials and keep query examples in YAML/JSON files outside versioned secrets. Respect `.gitignore` and avoid editing `dist/` outputs directly.
