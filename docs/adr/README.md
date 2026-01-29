# Architecture Decision Records

<!-- AI: Scan this index first. Only read full ADRs when relevant to your task. Each ADR has a "Rules" section at the top for quick reference. -->

## Reading Guide

**For AI assistants**: Each ADR has a `## Rules` section immediately after the header. Read that section for actionable constraints. Only read Context/Decision/Consequences if you need deeper understanding.

**For humans**: Read the full ADR. The Rules section is a summary, not a replacement.

## Index

| ADR | Title | Summary |
|-----|-------|---------|
| [000](adr-000-architectural-principles.md) | Architectural Principles | Protocol-agnostic core, cognitive separation, observable/evaluable by default, append-only memory, human sovereignty, learning-first |
| [001](adr-001-coding-assistant-agnosticism.md) | Coding Assistant Agnosticism | Single canonical AI config source; tool-specific files are generated |
| [002](adr-002-ci-cd-agnosticism.md) | CI/CD Platform Agnosticism | Logic in scripts not workflows; Makefile as standard interface; local/CI parity |
| [003](adr-003-python-tooling.md) | Python Tooling | uv + pyproject.toml + nox + Makefile + ruff + pytest |

## Quick Reference: All Rules

### From ADR-000 (Architectural Principles)
- Protocol-agnostic core: orchestration uses abstract roles/phases, not Six Hats specifics
- Agents think, orchestrators coordinate—never mix
- Every LLM call, contribution, and state mutation must be traced
- Reasoning artifacts structured for automated evaluation
- Append-only memory: never overwrite thinking
- Human sovereignty: pause, override, inject at any point
- LLM providers behind interfaces; prompts are config
- Partial results over crashes; failures logged with context

### From ADR-001 (Coding Assistant Agnosticism)
- Single canonical AI config source; `.cursor/rules`, `CLAUDE.md` are generated
- Use each tool's full capabilities; transformation handles differences
- Architecture lives in ADRs; AI config references them

### From ADR-002 (CI/CD Agnosticism)
- CI workflows are thin; logic lives in Makefile → task runner
- All commands identical locally and in CI
- No proprietary CI features without abstraction
- Standard interface: `make test`, `make lint`, `make build`

### From ADR-003 (Python Tooling)
- uv for packages/environments
- pyproject.toml as single config (no setup.py, requirements.txt)
- nox for task automation
- Makefile as standard interface
- ruff for linting/formatting
- pytest for testing

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
