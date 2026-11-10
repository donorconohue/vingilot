.PHONY: build lint check release

build:
	uv run --locked python tools/build-starship-config

lint:
	uv run --locked ruff check .
	uv run --locked ruff format --check .
	uv run --locked python tools/lint-starship-config starship/generated/vingilot.toml

check: lint
	uv run --locked pytest -q

release: check
	uv run --locked python tools/build-release
