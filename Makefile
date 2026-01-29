# Makefile - Standard interface for all build/test/lint operations
# See ADR-002 (CI/CD Agnosticism) and ADR-003 (Python Tooling)

# AI assistant CLI for slash commands (override with: CALL_SLASH_COMMAND="cursor -p" make adr-check)
CALL_SLASH_COMMAND ?= claude -p

.PHONY: help install test lint format adr-check adr-suggest configure-assistant-claude configure-assistant-cursor configure-assistant-all clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync

test:  ## Run tests
	uv run nox -s test

lint:  ## Run linter
	uv run nox -s lint

format:  ## Format code
	uv run nox -s format

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

clean:  ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
