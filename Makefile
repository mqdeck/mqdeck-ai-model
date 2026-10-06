.PHONY: setup prepare train evaluate export build test lint clean

VERSION ?=
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

setup:
	./scripts/setup.sh
prepare:
	./scripts/prepare.sh
train:
	@test -n "$(VERSION)" || (echo "VERSION is required: make train VERSION=0.1.0"; exit 2)
	./scripts/train.sh --version "$(VERSION)"
evaluate:
	@test -n "$(VERSION)" || (echo "VERSION is required: make evaluate VERSION=0.1.0"; exit 2)
	./scripts/evaluate.sh --version "$(VERSION)"
export:
	@test -n "$(VERSION)" || (echo "VERSION is required: make export VERSION=0.1.0"; exit 2)
	./scripts/export.sh --version "$(VERSION)"
build:
	@test -n "$(VERSION)" || (echo "VERSION is required: make build VERSION=0.1.0"; exit 2)
	./scripts/build-model.sh --version "$(VERSION)"
test:
	$(PYTHON) -m pytest
lint:
	$(PYTHON) -m ruff check pipeline training export tests
	$(PYTHON) -m black --check pipeline training export tests
	$(PYTHON) -m mypy pipeline training export
clean:
	./scripts/clean.sh
