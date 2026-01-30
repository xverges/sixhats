# Architecture Decision Records

<!-- AI: Run `python3 scripts/adr-list.py` to get accepted ADRs with their rules. Only read full ADRs when relevant to your task. -->

## Reading Guide

**For AI assistants**: Run `/adr-list` or `uv run scripts/adr-list.py` to get accepted ADRs and their rules. Only read full ADR files when you need deeper context.

**For humans**: Run `uv run scripts/adr-list.py` or browse the `adr-*.md` files directly.

## ADR Format

Each ADR follows this structure:

```markdown
# ADR-NNN: Title

**Status:** Proposed | Accepted | Deprecated | Superseded
**Date:** YYYY-MM-DD

## Rules

<!-- AI: This section contains actionable constraints. Read this first. -->

1. **Rule name**: Brief actionable constraint
2. **Another rule**: Keep to 4-9 bullet points

## Context

Why this decision was needed. Background, constraints, forces at play.

## Decision

What we decided and how it works. The detailed explanation.

## Consequences

### Benefits
- What we gain

### Costs
- What we trade off

## References

- Links to related ADRs, external docs
```

### Section purposes

| Section | For humans | For AI | Token cost |
|---------|------------|--------|------------|
| **Rules** | Quick reminder | Primary reference | Low (~10 lines) |
| **Context** | Understanding why | Skip unless debugging | Medium |
| **Decision** | Full details | Read when implementing | High |
| **Consequences** | Tradeoff awareness | Skip unless asked | Medium |
