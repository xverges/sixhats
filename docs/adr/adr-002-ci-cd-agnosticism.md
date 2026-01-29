# ADR-002: CI/CD Platform Agnosticism

**Status:** Accepted
**Date:** 2025-01-29

## Context

This project requires continuous integration and deployment automation. The CI/CD landscape includes GitHub Actions, GitLab CI, CircleCI, Jenkins, and others with varying features and lock-in levels.

We want the freedom to switch platforms without rewriting our automation. Build and test logic should be portable and runnable locally.

## Decision

Build and deployment workflows must remain portable:

### 1. Logic in Scripts, Not Workflows

- CI workflow files are **thin orchestration layers** that only call commands
- A **standard interface** (e.g., `Makefile`) provides consistent entry points (`make test`, `make lint`, `make build`)
- The standard interface delegates to **task runners** (e.g., `nox`, `npm scripts`) that contain the actual logic
- All commands must run identically locally and in CI

### 2. Avoid Platform-Specific Features

- No reliance on proprietary CI features (platform-specific caching, matrix syntax, reusable workflows) without abstraction
- If platform features are used, document the equivalent for other platforms

### 3. Standard Interfaces

- Use conventional environment variables (`CI`, `GITHUB_SHA`, etc.) through an abstraction layer if needed
- Artifacts use standard formats (tarballs, container images)

### 4. Local Reproducibility

- Developers run the same commands as CI: `make test`, `make lint`, etc.
- "Works on CI" is not an acceptable state if it doesn't work locally
- The layered approach (CI → Makefile → task runner) ensures parity

## Consequences

### Benefits

- **Freedom to switch**: Can move to different CI platforms as needs change
- **Local development**: Developers can run full builds without pushing
- **Debugging**: CI failures are reproducible locally
- **Reduced vendor risk**: No platform can hold the project hostage

### Costs

- **Feature limitations**: Can't use advanced platform-specific features freely
- **More scripting**: Thin CI files mean maintaining Makefile + task runner code
- **Discipline required**: Easy to accidentally introduce platform-specific dependencies
- **Some duplication**: May need equivalent configs for multiple platforms

## References

- [ADR-000](./adr-000-architectural-principles.md): Foundational principles
- [ADR-001](./adr-001-coding-assistant-agnosticism.md): Coding assistant agnosticism (related tooling decision)
- [ADR-003](./adr-003-python-tooling.md): Python tooling choices (implements this ADR)
