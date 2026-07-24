# neuromorphopy

A lightweight CLI tool and library for searching and downloading neuron morphologies from
[NeuroMorpho.org](https://neuromorpho.org/). Python 3.11+, packaged with `uv` and `hatchling`,
published to PyPI as `neuromorphopy`.

## Commands

`just` is the task runner; every recipe wraps `uv run`, so use `uv run …` directly if `just`
is unavailable.

```bash
just install     # uv sync + prek install
just check       # ruff format, ruff check, ty
just test        # pytest
just docs        # mkdocs dev server
just docs-test   # mkdocs build --strict
just update      # uv lock --upgrade + prek autoupdate
```

Before opening a PR, `just check && just test && just docs-test` must all pass — CI runs the
same three.

## Layout

| Path | Contents |
| --- | --- |
| `neuromorphopy/api.py` | `NeuroMorphoClient` — async httpx client, concurrent pagination and SWC downloads |
| `neuromorphopy/query.py` | `Query` / `QueryFields` plus the pydantic models validating query files |
| `neuromorphopy/cli.py` | Typer app: `fields`, `preview`, `download`, `validate` |
| `neuromorphopy/io/swc.py` | SWC URL resolution and file parsing |
| `neuromorphopy/utils/` | `api_utils.py` (SSL context, endpoints, metadata cleaning), `logging.py` |
| `neuromorphopy/exceptions.py` | `NeuroMorphoError` and subclasses |
| `tests/` | pytest suite; fixtures in `conftest.py` |
| `docs/` | mkdocs sources, published to Read the Docs |

The public surface is whatever `neuromorphopy/__init__.py` re-exports in `__all__`. Adding to
it is an API commitment — prefer keeping helpers private.

## Conventions specific to this repo

**Logging goes through `get_logger()`, never the `logging` module directly.** `setup_logging()`
configures a named `neuromorphopy` logger, so a bare `logging.info(...)` bypasses the CLI's
`--verbose`, `--quiet`, and `--log-to-file` flags entirely. Ruff's `LOG` rules are selected to
catch this; `tests/test_logging.py` guards it.

**Lint follows ruff's default rule set — no `select` list.** This is deliberate: the project
tracks current ruff defaults rather than a frozen snapshot. The tradeoff is that a ruff upgrade
can surface new rules (the 0.11 → 0.16 bump surfaced 22), so treat `just update` as a change that
may need code fixes, not a no-op bump. Fix what it reports; reach for a rule-specific `# noqa:
RULE - reason` only where the flagged behavior is genuinely intended, as with the deliberately
broad `except Exception` guards that keep one failed neuron from aborting a batch download.

**Hooks run under `prek`, not `pre-commit`.** The dev dependency is `prek`; `uv run pre-commit`
will fail. `.pre-commit-config.yaml` is still the config file — that is prek's format too.

**Tagging and publishing must stay in one workflow.** GitHub does not trigger workflow runs from
events created with the default `GITHUB_TOKEN`, so a tag pushed by CI cannot start a separate
publish workflow. See `docs/development/releasing.md`.

**The NeuroMorpho API needs a relaxed SSL context.** `get_neuromorpho_ssl_context()` exists
because the upstream server negotiates legacy TLS. Do not "fix" it by removing the custom
context.

## Ignored paths

`notebooks/`, `dist/`, `site/`, and `data/` are gitignored scratch or build output — never commit
them. `docs/agents/` is a gitignored symlink to agent-facing notes and must not become a real
directory.

## Testing

Pytest is rooted at `tests/` with `test_*.py` naming. Network calls are mocked via `pytest-mock`
— tests must not hit NeuroMorpho.org. Behavior changes need a test that fails before the fix.
