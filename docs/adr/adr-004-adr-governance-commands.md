# ADR-004: ADR Governance Commands

**Status:** Accepted
**Date:** 2025-01-29

## Rules

<!-- AI: This section contains actionable constraints. Read this first. -->

1. **`/adr-check`**: Run before committing to evaluate changes against accepted ADRs
2. **`/adr-suggest`**: Run periodically to detect patterns that may need new ADRs
3. **Canonical source**: Command definitions live in `.ai/commands/`

## Context

As the project evolves, we need mechanisms to prevent architectural drift. Manual review is inconsistent. We want automated checks that:
- Evaluate code changes against approved ADRs
- Detect emerging patterns that may warrant new ADRs
- Work within the coding assistant (fast feedback, no infrastructure)

## Decision

### Slash Commands

Two slash commands provide architectural governance:

**`/adr-check`** - Evaluates changes against accepted ADRs
- Reads ADRs with `Status: Accepted`, extracts Rules sections
- Analyzes git diff for the requested scope
- Reports violations, warnings, and observations

**`/adr-suggest`** - Detects patterns that may need ADRs
- Analyzes code for recurring patterns not yet documented
- Suggests new ADR titles and rationale

### Command Definitions

Commands are defined as markdown files in `.ai/commands/`:
- `adr-check.md` - Instructions for compliance evaluation
- `adr-suggest.md` - Instructions for pattern detection

Per ADR-001, tool-specific files (`.claude/commands/`) are generated from this canonical source.

## Consequences

### Benefits

- Fast feedback loop (runs in assistant, no infrastructure)
- Catches drift before it accumulates
- Encourages ADR maintenance

### Costs

- Manual invocation required
- LLM output may vary between runs

## References

- [ADR-001](./adr-001-coding-assistant-agnosticism.md): Canonical source pattern
