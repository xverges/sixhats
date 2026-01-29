# ADR Compliance Check

Evaluate code changes against approved Architecture Decision Records.

## Instructions

1. Read all ADR files from `docs/adr/adr-*.md`
2. Filter to ADRs with `Status: Accepted`
3. For each accepted ADR, extract the **Rules** section
4. Get the git diff for the requested scope (default: staged changes)
5. Analyze the diff against ADR rules and report findings

## Scope Options

- **staged** (default): `git diff --cached`
- **branch**: `git diff main...HEAD`
- **commit <sha>**: `git show <sha>`
- **all**: Full codebase audit against rules

## Output Format

For each finding, report:

```
### [VIOLATION|WARNING|INFO] ADR-NNN: Principle Name

**File:** path/to/file.py:L10-15
**Issue:** Description of the concern
**Evidence:** `the code that triggered this`
**Suggestion:** How to resolve (if applicable)
```

End with a summary:

```
## Summary

- Violations: N
- Warnings: N
- Info: N

[Brief assessment]
```

## Evaluation Guidelines

- **VIOLATION**: Clear breach of an accepted rule
- **WARNING**: Potential concern warranting discussion
- **INFO**: Observation that may be relevant

Focus on architectural concerns, not code style. Not every change needs findings.
