set shell := ["bash", "-c"]

# list all commands (default)
default:
  @just --list

# install the virtual environment and pre-commit hooks
install:
  @echo "📦 Creating virtual environment"
  @uv sync --all-extras --locked --python=3.13
  @echo "🛠️ Installing developer tools..."
  @uv run pre-commit install

# run code quality tools
check:
  @echo "🧹 Formatting code: Running ruff format (check)"
  @uv run ruff format
  @echo "⚡️ Linting code: Running ruff check"
  @uv run ruff check .
  @echo "🔎 Type checking: Running ty"
  @uv run ty check .

# run pytest
test:
  @echo "✅ Testing code: Running pytest"
  @uv run pytest

# build and serve the documentation
docs:
  @uv run mkdocs serve

# test if documentation can be built without warnings or errors
docs-test:
  @echo "⚙️ Testing documentation build"
  @uv run mkdocs build --strict

# update pre-commit hooks
update:
  @echo "⚙️ Updating dependencies and pre-commit hooks"
  @uv lock --upgrade
  @uv run pre-commit autoupdate

# list all commands
help:
  @just --list
