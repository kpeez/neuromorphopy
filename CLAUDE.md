# neuromorphopy

CLI + library for downloading neuron morphologies from NeuroMorpho.org. Python 3.11+, `uv` + `hatchling`, published to PyPI.

## Commands

```bash
just install     # uv sync + prek install
just check       # ruff format + ruff check + ty
just test        # pytest
just docs        # mkdocs dev server
just docs-test   # mkdocs build --strict
just update      # uv lock --upgrade + prek autoupdate
```

`just check && just test && just docs-test` must pass before a PR — CI runs the same three.

## Layout

- `api.py` — `NeuroMorphoClient`; async httpx, concurrent pagination + SWC download
- `query.py` — `Query` / `QueryFields`; pydantic validation of query files
- `cli.py` — Typer app: `fields`, `preview`, `download`, `validate`
- `io/swc.py` — SWC URL resolution and parsing
- `utils/` — `api_utils.py` (SSL, endpoints, metadata), `logging.py`

Public API is `__init__.py`'s `__all__`. Adding to it is a commitment; keep helpers private.

## Gotchas

- **Log via `get_logger()`, never `logging.*`.** `setup_logging()` configures a named `neuromorphopy` logger; root-logger calls silently bypass `--verbose`/`--quiet`/`--log-to-file`. Guarded by `tests/test_logging.py`.
- **Hooks are `prek`, not `pre-commit`** — `uv run pre-commit` fails. `.pre-commit-config.yaml` is still the config file.
- **prek stashes unstaged changes before running hooks**, so they see only staged files. A commit changing lint config must also carry the code that satisfies it, or the hook fails.
- **Write commit messages to a file and use `git commit -F <file>`** — `-F -` with a heredoc silently no-ops under the hook.
- **Ruff tracks upstream defaults; there is no `select`.** So `just update` can surface new rules and is not a no-op bump. Prefer real fixes over `# noqa: RULE - reason`.
- **Tagging and publishing must stay in one workflow.** GitHub won't trigger workflow runs from `GITHUB_TOKEN` events, so a CI-pushed tag can't start a separate publish run. See `docs/development/releasing.md`.
- **Don't "fix" `get_neuromorpho_ssl_context()`** — NeuroMorpho negotiates legacy TLS and needs the relaxed context.
- **Datetimes that build filenames use `.astimezone()`, not UTC** — switching them silently renames every log file and download dir.

## Conventions

- Tests live in `tests/test_*.py`; network is mocked with `pytest-mock` — never hit NeuroMorpho.org. Behavior changes need a test that fails first.
- Never commit `notebooks/`, `dist/`, `site/`, `data/`. `docs/agents/` is a gitignored symlink and must never become a real directory.
