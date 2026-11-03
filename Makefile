# this_file: Makefile
.PHONY: dev install test lint format build release

dev install:
	uv sync --frozen

test:
	./test.sh

lint:
	uv run ruff check src tests scripts hatch_build.py
	uv run ruff format --check src tests scripts hatch_build.py

format:
	uv run ruff check --fix src tests scripts hatch_build.py
	uv run ruff format src tests scripts hatch_build.py

build:
	./scripts/build.sh

release:
	./publish.sh
