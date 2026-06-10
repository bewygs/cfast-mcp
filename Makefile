.PHONY: help

help:
	@echo "Usage:"
	@echo "  make install      Install the package with dev dependencies"
	@echo "  make run          Run the MCP server"
	@echo "  make test         Run all tests (CFAST-dependent ones skip if no binary)"
	@echo "  make test-local   Run only the tests requiring the CFAST binary"
	@echo "  make cov          Run tests with coverage report"
	@echo "  make check        Lint the code with ruff"
	@echo "  make format       Format the code with ruff"
	@echo "  make type         Type check the code with mypy"
	@echo "  make clean        Clean build artifacts and cache"
	@echo "  make pre-commit   Run pre-commit hooks"
	@echo "  make allci        Run all CI steps (check, format, type, test)"

install:
	uv sync --extra dev

run:
	uv run cfast-mcp

test:
	uv run pytest

test-local:
	uv run pytest -m local

cov:
	uv run pytest --cov

check:
	uv run ruff check --fix .

format:
	uv run ruff format .

type:
	uv run mypy src/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

pre-commit:
	uv run pre-commit run --all-files

allci: check format type cov
	@echo "All CI steps completed!"
