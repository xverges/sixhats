# ADR List

List all accepted Architecture Decision Records with their rules.

## Instructions

Run the deterministic script to get the current list of accepted ADRs:

```bash
uv run scripts/adr-list.py
```

This outputs all ADRs with `Status: Accepted`, including their Rules sections.

## Usage

Use this command to:
- Get the authoritative list of active architectural decisions
- Review all rules before implementing changes
- Provide context to other ADR commands (`/adr-check`, `/adr-suggest`)

## Output Format

```
# Accepted ADRs (N total)

## ADR-NNN: Title
**File:** adr-NNN-slug.md

### Rules
1. **Rule name**: Description
...
```
