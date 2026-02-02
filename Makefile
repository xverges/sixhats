# Makefile for sixhats
#
# Standard interface for CI/CD per ADR-002 and ADR-003.
# Architecture: Makefile → nox → uv
#
# All commands run identically locally and in CI.

# AI assistant CLI for slash commands (override with: CALL_SLASH_COMMAND="cursor -p" make adr-check)
CALL_SLASH_COMMAND ?= claude -p

.PHONY: help install test lint typecheck format check clean adr-check adr-suggest configure-assistant-claude configure-assistant-cursor configure-assistant-all

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync --dev

test:  ## Run test suite
	uv run nox -s test

lint:  ## Run linter (ruff check)
	uv run nox -s lint

typecheck:  ## Run type checker (pyright)
	uv run nox -s typecheck

format:  ## Format code (ruff format)
	uv run nox -s format

check: lint typecheck test

clean:  ## Remove build artifacts
	rm -rf .nox .pytest_cache .ruff_cache __pycache__ .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

adr-check:  ## Check staged changes against ADRs
	$(CALL_SLASH_COMMAND) "/adr-check"

adr-suggest:  ## Detect patterns that may need new ADRs
	$(CALL_SLASH_COMMAND) "/adr-suggest"

configure-assistant-claude:  ## Generate Claude Code slash commands
	@chmod +x scripts/configure-assistant.sh
	@./scripts/configure-assistant.sh claude

configure-assistant-cursor:  ## Generate Cursor rules (not yet implemented)
	@chmod +x scripts/configure-assistant.sh
	@./scripts/configure-assistant.sh cursor

configure-assistant-all:  ## Generate all AI assistant configs
	@chmod +x scripts/configure-assistant.sh
	@./scripts/configure-assistant.sh all
