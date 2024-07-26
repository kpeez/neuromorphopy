.PHONY: check_uv, install install_dev check test docs docs_test update help

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
		uv pip compile pyproject.toml -o requirements.txt && \
		uv pip install -r requirements.txt && \
		uv pip install -e . && \
		pre-commit install

install_dev: check_uv ## Install the virtual environment and  pre-commit hooks
	@echo "📦 Creating virtual environment"
	@uv venv --seed
	@echo "📦 Installing dependencies"
	@. .venv/bin/activate && \
		uv pip compile pyproject.toml -o requirements-dev.txt --extra=dev && \
		uv pip install -r requirements-dev.txt && \
		uv pip install -e . && \
		echo "📦 Installing pre-commit and mypy.." && \
		pre-commit install && \
		mypy --install-types --non-interactive

check: ## Run code quality tools
	@echo "🔒 Compiling requirements from 'pyproject.toml':"
	@uv pip compile -o requirements.txt pyproject.toml
	@uv pip compile -o requirements-dev.txt --extra=dev pyproject.toml
	@. .venv/bin/activate && \
		echo "⚡️ Linting code: Running ruff" && \
		ruff check . && \
		echo "🧹 Checking code: Running pre-commit" && \
		pre-commit run --all-files && \
		echo "🔬 Static type checking: Running mypy" && \
		mypy .

test: ## Test the code with pytest
	@echo "✅ Testing code: Running pytest"
	@. .venv/bin/activate && \
	pytest

docs: ## Build and serve the documentation
	@. .venv/bin/activate && \
	mkdocs serve

docs_test: ## Test if documentation can be built without warnings or errors
	@echo "⚙️ Testing documentation build"
	@. .venv/bin/activate && \
		mkdocs build --strict

update: ## Update pre-commit hooks
	@echo "⚙️ Updating environment and pre-commit hooks"
	@. .venv/bin/activate && \
		pre-commit autoupdate

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
