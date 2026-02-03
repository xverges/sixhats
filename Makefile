# Makefile for sixhats
#
# Standard interface for CI/CD per ADR-002 and ADR-003.
# Architecture: Makefile → nox → uv
#
# All commands run identically locally and in CI.

# AI assistant CLI for slash commands (override with: CALL_SLASH_COMMAND="cursor -p" make adr-check)
CALL_SLASH_COMMAND ?= claude -p

.PHONY: adr-check adr-suggest check clean configure-assistant-all configure-assistant-antigravity configure-assistant-claude configure-assistant-cursor format help install lint test typecheck validate-agents

# --- Help ---

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# --- Development ---

format:  ## Format code (ruff format)
	uv run nox -s format

install:  ## Install dependencies
	uv sync --dev

lint:  ## Run linter (ruff check)
	uv run nox -s lint

test:  ## Run test suite
	uv run nox -s test

typecheck:  ## Run type checker (pyright)
	uv run nox -s typecheck

# --- Quality Assurance ---

check: lint typecheck test validate-agents  ## Run lint, typecheck, test, and validate AGENTS.md

validate-agents:  ## Validate .ai/AGENTS.md is in sync
	@./scripts/validate-agents-md.sh

# --- Maintenance ---

clean:  ## Remove build artifacts
	rm -rf .nox .pytest_cache .ruff_cache __pycache__ .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# --- ADR Tools ---

adr-check:  ## Check staged changes against ADRs
	$(CALL_SLASH_COMMAND) "/adr-check"

adr-suggest:  ## Detect patterns that may need new ADRs
	$(CALL_SLASH_COMMAND) "/adr-suggest"

# --- Assistant Configuration ---

configure-assistant-all:  ## Generate all AI assistant configs
	@chmod +x scripts/configure-assistant.sh
	@./scripts/configure-assistant.sh all

configure-assistant-claude:  ## Generate Claude Code slash commands
	@chmod +x scripts/configure-assistant.sh
	@./scripts/configure-assistant.sh claude

configure-assistant-cursor:  ## Generate Cursor rules (not yet implemented)
	@chmod +x scripts/configure-assistant.sh
	@./scripts/configure-assistant.sh cursor
