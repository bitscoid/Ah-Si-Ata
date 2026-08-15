# Makefile for Ah-Si-Ata
#
# Usage:
#   make setup   - full setup: system deps, venv, python deps, .env
#   make run     - run the app (auto-bootstraps if needed)
#   make install - (re)install python dependencies into the venv
#   make env     - create .env from .env.template if missing
#   make update  - git pull --rebase
#   make clean   - remove venv and python caches
#   make help    - show this help

PY          ?= python3
VENV        := venv
PYBIN       := $(VENV)/bin/python
PIP         := $(PYBIN) -m pip
STAMP       := $(VENV)/.setup-stamp

.PHONY: help setup install run env update clean

help:
	@echo "Ah-Si-Ata Makefile"
	@echo ""
	@echo "  make setup    - full setup: system deps, venv, python deps, .env"
	@echo "  make run      - run the app (auto-setup if venv is missing/stale)"
	@echo "  make install  - (re)install python dependencies into venv"
	@echo "  make env      - create .env from .env.template if missing"
	@echo "  make update   - git pull --rebase"
	@echo "  make clean    - remove venv, __pycache__ and .ruff_cache"

setup:
	@bash setup.sh
	@touch $(STAMP)

# Rebuild the venv whenever setup.sh or requirements.txt change.
$(STAMP): setup.sh requirements.txt
	@bash setup.sh
	@touch $(STAMP)

install: $(STAMP)
	$(PIP) install -r requirements.txt

run: $(STAMP)
	@test -f .env || { cp .env.template .env; echo "==> Created .env from .env.template"; }
	@$(PYBIN) main.py

env:
	@if [ ! -f .env ]; then \
		cp .env.template .env; \
		echo "==> Created .env from .env.template"; \
	else \
		echo ".env already exists"; \
	fi

update:
	@git pull --rebase

clean:
	@rm -rf $(VENV) .ruff_cache
	@find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned."