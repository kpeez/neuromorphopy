.PHONY: install
install: ## Install the poetry environment and install the pre-commit hooks
	@echo "📦 Creating virtual environment using poetry"
	@poetry install	
	@poetry run pre-commit install
	@poetry shell

.PHONY: check
check: ## Run code quality tools.
	@echo "🔒 Checking Poetry lock file consistency with 'pyproject.toml': Running poetry lock --check"
	@poetry lock --check
	@echo "🧹 Linting code: Running pre-commit"
	@poetry run pre-commit run -a
	@echo "🔬 Static type checking: Running mypy"
	@poetry run mypy

.PHONY: test
test: ## Test the code with pytest
	@echo "✅ Testing code: Running pytest"
	@poetry run pytest --doctest-modules

.PHONY: build
build: clean-build ## Build wheel file using poetry
	@echo "🛞 Creating wheel file"
	@poetry build

.PHONY: clean-build
clean-build: ## clean build artifacts
	@rm -rf dist

.PHONY: docs
docs: ## Build and serve the documentation
	@poetry run mkdocs serve

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@poetry run mkdocs build -s

.PHONY: update	
update: ## Update the poetry environment and pre-commit hooks
	@echo "⚙️  Updating poetry environment and pre-commit hooks"
	@poetry update
	@poetry run pre-commit autoupdate

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help