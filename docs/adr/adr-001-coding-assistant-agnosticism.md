# ADR-001: Coding Assistant Agnosticism

**Status:** Accepted
**Date:** 2025-01-29

## Rules

<!-- AI: This section contains actionable constraints. Read this first. -->

1. **Canonical source**: AI assistant config lives in a single source of truth, tool-specific files are generated
2. **Full utilization**: Use each tool's full capabilities; transformation layer handles differences
3. **Documentation primary**: Architecture lives in ADRs, AI config references them (no duplication)
4. **Generated files**: `.cursor/rules`, `CLAUDE.md`, etc. are outputs, not sources

## Context

This project uses AI coding assistants for development. The landscape is evolving rapidly with Claude Code, Cursor, GitHub Copilot, Codeium, and others competing with different capabilities and pricing.

We are actively exploring alternatives and want the freedom to switch tools without major rework. This aligns with our learning-first philosophy—we should understand our tools, not be captive to them.

However, we do NOT want "least common denominator" agnosticism. We want to:
- Fully configure whichever assistant we use
- Share AI context across the team
- Switch assistants through automation, not manual reconfiguration

## Decision

The codebase uses a **canonical configuration** that can be transformed into tool-specific formats:

### 1. Canonical Source, Generated Targets

- A single source of truth for AI assistant configuration lives in version control
- Tool-specific files (`.cursor/rules`, `CLAUDE.md`, etc.) are generated via scripts
- Generated files may use symbolic links or transformations from the canonical source
- The generation script lives in `scripts/` and is documented

### 2. Full Tool Utilization

- Use each assistant's full capabilities—don't artificially limit to common features
- Tool-specific optimizations are acceptable when they provide significant value
- The transformation layer handles differences between tools

### 3. Documentation Remains Primary

- Architecture decisions live in ADRs, not only in AI prompts
- The canonical AI config should reference ADRs, not duplicate them
- Any context an AI needs should be useful to a human reader too

### 4. Switching Protocol

- Switching assistants means: (1) run generation script for new tool, (2) update any tool-specific optimizations
- The canonical config captures what matters; tool-specific quirks are handled in transformations

## Consequences

### Benefits

- **Freedom to switch**: Automation makes switching assistants tractable
- **Shared context**: Team shares AI configuration through the canonical source
- **Full capability**: Not limited to lowest common denominator
- **Single source of truth**: One place to update AI context

### Costs

- **Transformation maintenance**: Must maintain scripts that generate tool-specific configs
- **Sync discipline**: Generated files must stay in sync with canonical source
- **Tool knowledge**: Need to understand each tool's config format to write transformations

## References

- [ADR-000](./adr-000-architectural-principles.md): Foundational principles (learning-first philosophy)
- [ADR-002](./adr-002-ci-cd-agnosticism.md): CI/CD platform agnosticism (related tooling decision)
