#!/usr/bin/env bash
# Generate tool-specific AI assistant configuration from canonical source.
# See ADR-001 (Coding Assistant Agnosticism).
#
# Usage: ./scripts/configure-assistant.sh [tool]
#   tool: claude (default), cursor, antigravity, all

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

generate_antigravity() {
    echo "Generating Antigravity configuration..."

    # 1. Create .agent/README.md symlink to canonical AGENTS.md
    local agents_md="${REPO_ROOT}/.ai/AGENTS.md"
    local agent_readme="${REPO_ROOT}/.agent/README.md"

    if [[ -f "$agents_md" ]]; then
        mkdir -p "${REPO_ROOT}/.agent"
        rm -f "$agent_readme"
        ln -sf "../.ai/AGENTS.md" "$agent_readme"
        echo "  .agent/README.md -> .ai/AGENTS.md"
    else
        echo "  Warning: .ai/AGENTS.md not found, skipping .agent/README.md"
    fi

    # 2. Transform commands to workflows (Antigravity uses YAML frontmatter)
    local target_dir="${REPO_ROOT}/.agent/workflows"
    mkdir -p "$target_dir"

    # Remove existing workflow files
    rm -f "$target_dir"/*.md 2>/dev/null || true

    # Transform each command to workflow format
    for cmd in "$CANONICAL_DIR"/*.md; do
        if [[ -f "$cmd" ]]; then
            local basename
            basename=$(basename "$cmd")
            local target="${target_dir}/${basename}"
            
            # Extract title from first heading (assumes "# Title" format)
            local title
            title=$(grep -m 1 '^# ' "$cmd" | sed 's/^# //' || echo "Command")
            
            # Create workflow with YAML frontmatter
            {
                echo "---"
                echo "description: ${title}"
                echo "---"
                tail -n +2 "$cmd"  # Skip the first line (title) from original
            } > "$target"
            
            echo "  /${basename%.md} -> .agent/workflows/${basename}"
        fi
    done

    echo ""
    echo "Done. Configuration generated:"
    echo "  - .agent/README.md (project context)"
    if [[ -d "$target_dir" ]]; then
        for workflow in "$target_dir"/*.md; do
            if [[ -f "$workflow" ]]; then
                local name
                name=$(basename "$workflow" .md)
                echo "  - /${name} (workflow)"
            fi
        done
    fi
}

case "${1:-claude}" in
    claude)
        generate_claude
        ;;
    cursor)
        generate_cursor
        ;;
    antigravity)
        generate_antigravity
        ;;
    all)
        generate_claude
        generate_cursor
        generate_antigravity
        ;;
    *)
        echo "Usage: $0 [claude|cursor|antigravity|all]"
        exit 1
        ;;
esac
