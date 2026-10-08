.PHONY: help setup run prepare train evaluate export build test lint clean

VERSION ?= 0.1.0
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

help:
	@echo "MQDeck AI commands"
	@echo "  make run                  Prepare Ubuntu GPU host and build everything"
	@echo "  make build                Build model on an already prepared host"
	@echo "  make prepare              Prepare and validate the dataset"
	@echo "  make test                 Run unit tests"
	@echo "  VERSION=1.0.0 make build  Build a specific release version"

setup:
	./scripts/setup.sh
run:
	./scripts/run.sh --version "$(VERSION)"
prepare:
	./scripts/prepare.sh
train:
	./scripts/train.sh --version "$(VERSION)"
evaluate:
	./scripts/evaluate.sh --version "$(VERSION)"
export:
	./scripts/export.sh --version "$(VERSION)"
build:
	./scripts/build.sh --version "$(VERSION)"
test:
	$(PYTHON) -m pytest
lint:
	$(PYTHON) -m ruff check pipeline training export tests
	$(PYTHON) -m black --check pipeline training export tests
	$(PYTHON) -m mypy pipeline training export
clean:
	./scripts/clean.sh
