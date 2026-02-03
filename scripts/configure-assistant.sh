#!/usr/bin/env bash
# Generate tool-specific AI assistant configuration from canonical source.
# See ADR-001 (Coding Assistant Agnosticism).
#
# Usage: ./scripts/configure-assistant.sh [tool]

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CANONICAL_DIR="${REPO_ROOT}/.ai/commands"

generate_claude() {
    echo "Generating Claude Code configuration..."

    # 1. Create CLAUDE.md symlink to canonical AGENTS.md
    local agents_md="${REPO_ROOT}/.ai/AGENTS.md"
    local claude_md="${REPO_ROOT}/CLAUDE.md"

    if [[ -f "$agents_md" ]]; then
        rm -f "$claude_md"
        ln -sf ".ai/AGENTS.md" "$claude_md"
        echo "  CLAUDE.md -> .ai/AGENTS.md"
    else
        echo "  Warning: .ai/AGENTS.md not found, skipping CLAUDE.md"
    fi

    # 2. Create slash command symlinks
    local target_dir="${REPO_ROOT}/.claude/commands"
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

    echo ""
    echo "Done. Configuration generated:"
    echo "  - CLAUDE.md (project context)"
    if [[ -d "$target_dir" ]]; then
        for cmd in "$target_dir"/*.md; do
            if [[ -f "$cmd" ]]; then
                local name
                name=$(basename "$cmd" .md)
                echo "  - /$name (slash command)"
            fi
        done
    fi
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
        exit 1
        ;;
esac
