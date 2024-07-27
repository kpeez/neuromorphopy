.PHONY: check_uv, install install-dev check test docs docs_test update help

check_uv: # install `uv` if not installed
	@if ! command -v uv &> /dev/null 2>&1; then \
		echo "uv is not installed, installing now..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	@uv self update

install: check_uv ## Install the virtual environment and  pre-commit hooks
	@echo "📦 Creating virtual environment"
	@uv venv --seed
	@echo "📦 Installing dependencies"
	@. .venv/bin/activate && \
		uv pip install -r requirements.txt && \
		uv pip install -e .

install-dev: check_uv ## Install the virtual environment and  pre-commit hooks
	@echo "📦 Creating virtual environment and install dependencies"
	@uv venv --seed && uv sync
	@uv pip compile pyproject.toml -o requirements.txt
	@echo "🛠️ Installing developer tools..."
	@uvx pre-commit install
	@. .venv/bin/activate && mypy --install-types --non-interactive

check: ## Run code quality tools
	@echo "🔒 Compiling requirements from 'pyproject.toml':"
	@uv pip compile -o requirements.txt pyproject.toml
	@echo "⚡️ Linting code: Running ruff"
	@uv run ruff check .
	@echo "🧹 Checking code: Running pre-commit"
	@uvx pre-commit run --all-files
	@echo "🔬 Static type checking: Running mypy"
	@uvx mypy .

test: ## Test the code with pytest
	@echo "✅ Testing code: Running pytest"
	@uvx pytest

docs: ## Build and serve the documentation
	@uvx mkdocs serve

docs-test: ## Test if documentation can be built without warnings or errors
	@echo "⚙️ Testing documentation build"
	@uvx mkdocs build --strict

update: ## Update pre-commit hooks
	@echo "⚙️ Updating environment and pre-commit hooks"
	@uvx pre-commit autoupdate

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
