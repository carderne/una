all: fmt lint check test

fmt:
	@uv run ruff format

fmt-check:
	@uv run ruff format --check

lint:
	@uv run ruff check --fix

lint-check:
	@uv run ruff check

check:
	@uv run basedpyright

test:
	@uv run pytest
