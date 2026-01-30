# ADR Emergence Detection

Identify patterns in the codebase that may warrant new Architecture Decision Records.

## Instructions

1. Run `uv run scripts/adr-list.py` to get accepted ADRs and their rules
2. Analyze the requested scope for recurring patterns
3. Identify decisions that are implicit in code but not documented
4. Suggest new ADRs where patterns appear 2+ times

## Scope Options

- **recent** (default): Last 10 commits
- **branch**: All changes on current branch vs main
- **directory <path>**: Specific directory
- **all**: Full codebase analysis

## What to Look For

- Repeated structural patterns (e.g., all services follow same structure)
- Implicit conventions (e.g., error handling approach, naming patterns)
- Technology choices not documented (e.g., specific libraries used consistently)
- Boundaries and interfaces (e.g., how modules communicate)

## Output Format

For each suggestion:

```
### Suggested ADR: [Title]

**Pattern observed:** What you noticed
**Frequency:** Where it appears (N locations)
**Rationale:** Why this warrants documentation
**Related ADRs:** Existing ADRs this relates to
**Evidence:**
- file1.py: description
- file2.py: description
```

End with:

```
## Summary

Found N patterns that may warrant ADRs.

[Brief assessment of documentation coverage]
```

## Guidelines

- Focus on architectural decisions, not implementation details
- Suggest ADRs for decisions that affect multiple files/modules
- Consider: if a new team member asked "why is it done this way?", would an ADR help?
