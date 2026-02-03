#!/usr/bin/env bash
# Validate that .ai/AGENTS.md references are still accurate.
# Run in CI to catch drift between documentation and reality.
#
# Usage: ./scripts/validate-agents-md.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_MD="${REPO_ROOT}/.ai/AGENTS.md"
ERRORS=0

echo "Validating .ai/AGENTS.md..."

# Check file exists
if [[ ! -f "$AGENTS_MD" ]]; then
    echo "ERROR: .ai/AGENTS.md not found"
    exit 1
fi

# 1. Check documented directories exist
echo ""
echo "Checking documented directories..."
declare -a DOCUMENTED_DIRS=(
    "src/agents"
    "src/workflows"
    "src/schemas"
    "src/services"
    "src/observability"
    "src/evals"
    "docs/adr"
    "scripts"
)

for dir in "${DOCUMENTED_DIRS[@]}"; do
    if [[ -d "${REPO_ROOT}/${dir}" ]]; then
        echo "  OK: ${dir}/"
    else
        echo "  MISSING: ${dir}/ (documented but doesn't exist)"
        ((ERRORS++))
    fi
done

# 2. Check for undocumented src/ subdirectories
echo ""
echo "Checking for undocumented src/ directories..."
for dir in "${REPO_ROOT}"/src/*/; do
    if [[ -d "$dir" ]]; then
        dirname=$(basename "$dir")
        if [[ "$dirname" == "__pycache__" ]]; then
            continue
        fi
        # Check for either "src/dirname" or just "dirname/" in the structure block
        if ! grep -qE "(src/${dirname}|${dirname}/)" "$AGENTS_MD" 2>/dev/null; then
            echo "  UNDOCUMENTED: src/${dirname}/ (exists but not in AGENTS.md)"
            ((ERRORS++))
        fi
    fi
done

# 3. Check documented commands match .ai/commands/
echo ""
echo "Checking documented commands..."
COMMANDS_DIR="${REPO_ROOT}/.ai/commands"

if [[ -d "$COMMANDS_DIR" ]]; then
    for cmd in "$COMMANDS_DIR"/*.md; do
        if [[ -f "$cmd" ]]; then
            cmdname=$(basename "$cmd" .md)
            if grep -q "/${cmdname}" "$AGENTS_MD" 2>/dev/null; then
                echo "  OK: /${cmdname}"
            else
                echo "  UNDOCUMENTED: /${cmdname} (exists but not in AGENTS.md)"
                ((ERRORS++))
            fi
        fi
    done
fi

# Summary
echo ""
if [[ $ERRORS -eq 0 ]]; then
    echo "Validation passed. AGENTS.md is in sync."
    exit 0
else
    echo "Validation failed. Found ${ERRORS} issue(s)."
    echo "Update .ai/AGENTS.md to fix (CLAUDE.md is a symlink)."
    exit 1
fi
