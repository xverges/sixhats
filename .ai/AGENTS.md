# Six Thinking Hats

A multi-agent implementation of Edward de Bono's Six Thinking Hats parallel thinking framework, built on dapr-agents.

## Quick Start for AI Assistants

1. **Get architecture rules**: Run `/adr-list` to see all accepted ADRs and their rules
2. **Read full ADRs only when needed**: ADRs are in [docs/adr/](docs/adr/)
3. **Check ADR compliance**: Run `/adr-check` before proposing changes

## Project Structure

```
src/
  agents/       # Hat agents (Black, White, Yellow, etc.)
  workflows/    # Dapr workflow orchestration
  schemas/      # Pydantic models (workspace, contributions)
  services/     # Business logic services
  observability/# Tracing and metrics
  evals/        # Evaluation framework
docs/adr/       # Architecture Decision Records (source of truth)
scripts/        # Build and maintenance scripts
```

## Key Patterns

- **dapr-agents**: All agent orchestration uses dapr-agents framework
- **ADR-driven**: Architecture decisions are documented in ADRs with explicit Rules sections
- **Workspace model**: Sessions use a structured workspace schema for state

## Commands

| Command | Purpose |
|---------|---------|
| `/adr-list` | List accepted ADRs with their rules |
| `/adr-check` | Check if proposed changes comply with ADRs |
| `/adr-suggest` | Detect if current work warrants a new ADR |

## Keeping This File Current

CI validates structure (`scripts/validate-agents-md.sh`). You should catch what CI cannot:

- **Key Patterns** no longer reflect how the codebase actually works
- **Directory descriptions** are inaccurate or misleading
- **Missing context** that would have helped you ramp up faster
- **Outdated terminology** or stale references to removed concepts

If you learn something important while working that would help future sessions, propose adding it here. Edit `.ai/AGENTS.md` directly.
