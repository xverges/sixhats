#!/usr/bin/env bash
# Generate tool-specific AI assistant configuration from canonical source.
# See ADR-001 (Coding Assistant Agnosticism) and ADR-004 (ADR Governance Commands).
#
# Usage: ./scripts/configure-assistant.sh [tool]
#   tool: claude (default), cursor, all

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CANONICAL_DIR="${REPO_ROOT}/.ai/commands"

generate_claude() {
    local target_dir="${REPO_ROOT}/.claude/commands"

    echo "Generating Claude Code slash commands..."
    mkdir -p "$target_dir"

    # Remove existing symlinks
    find "$target_dir" -type l -delete 2>/dev/null || true

    # Create symlinks from canonical source
    for cmd in "$CANONICAL_DIR"/*.md; do
        if [[ -f "$cmd" ]]; then
            local basename
            basename=$(basename "$cmd")
            ln -sf "../../.ai/commands/${basename}" "${target_dir}/${basename}"
            echo "  /${basename%.md} -> .ai/commands/${basename}"
        fi
    done

    echo "Done. Slash commands available:"
    for cmd in "$target_dir"/*.md; do
        if [[ -f "$cmd" ]]; then
            local name
            name=$(basename "$cmd" .md)
            echo "  /$name"
        fi
    done
}

generate_cursor() {
    echo "Cursor generation not yet implemented."
    echo "Add transformation logic here when needed."
}

case "${1:-claude}" in
    claude)
        generate_claude
        ;;
    cursor)
        generate_cursor
        ;;
    all)
        generate_claude
        generate_cursor
        ;;
    *)
        echo "Usage: $0 [claude|cursor|all]"
        exit 1
        ;;
esac
