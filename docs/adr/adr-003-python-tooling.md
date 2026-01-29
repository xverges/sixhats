# ADR-003: Python Tooling

**Status:** Accepted
**Date:** 2025-01-29

## Rules

<!-- AI: This section contains actionable constraints. Read this first. -->

1. **uv** for package/environment management (not pip, poetry)
2. **pyproject.toml** as single config source (no setup.py, requirements.txt)
3. **nox** for task automation (sessions are Python functions)
4. **Makefile** as standard interface: `make test` → `nox -s test`
5. **ruff** for linting and formatting (not flake8, black, isort)
6. **pytest** for testing

## Context

This is a Python project requiring standard development workflows: dependency management, virtual environments, testing, linting, and formatting. Per [ADR-002](./adr-002-ci-cd-agnosticism.md), we need a layered approach where CI workflows call a standard interface, which delegates to task runners.

The Python tooling landscape includes:
- **Package/environment management**: pip, poetry, pdm, uv
- **Project configuration**: setup.py, setup.cfg, pyproject.toml
- **Task runners**: tox, nox, invoke, make
- **Standard interfaces**: Makefile, shell scripts
- **Linting/formatting**: flake8, pylint, black, isort, ruff
- **Testing**: pytest, unittest, nose

Per our learning-first philosophy ([ADR-000](./adr-000-architectural-principles.md)), we want tools that are understandable, debuggable, and don't hide too much magic.

## Decision

### 1. uv for Package and Environment Management

- Fast Rust-based tool that replaces pip, pip-tools, and virtualenv
- Handles dependency resolution, installation, and virtual environment creation
- Drop-in compatible with standard Python packaging

### 2. pyproject.toml as Single Configuration Source

- PEP 621 standard for project metadata
- All tool configuration lives here (ruff, pytest, etc.)
- No setup.py, setup.cfg, or requirements.txt files

### 3. nox for Task Automation

- Session-based task runner where sessions are Python functions
- More flexible and debuggable than declarative tox configs
- Aligns with learning-first: it's just Python code we can understand and modify
- Handles testing across Python versions, linting, formatting, etc.

### 4. Makefile as Standard Interface

- Provides consistent entry points: `make test`, `make lint`, `make format`, `make build`
- Thin layer that delegates to nox sessions
- Works everywhere (CI, local dev, any platform with make)
- Implements [ADR-002](./adr-002-ci-cd-agnosticism.md)'s layered approach

### 5. ruff for Linting and Formatting

- Single tool replacing flake8, black, isort, and others
- Extremely fast (written in Rust)
- Configured entirely in pyproject.toml
- Handles both linting (`ruff check`) and formatting (`ruff format`)
- Aligns with learning-first: one tool to understand instead of four

### 6. pytest for Testing

- De facto standard Python testing framework
- Simple test discovery and execution
- Rich plugin ecosystem (pytest-cov, pytest-asyncio, etc.)
- Configured in pyproject.toml

### Layered Architecture

```
CI Workflow (GitHub Actions, etc.)
    │
    ▼
Makefile (standard interface)
    │  make test → nox -s test
    │  make lint → nox -s lint
    │  make format → nox -s format
    ▼
noxfile.py (task definitions)
    │
    ▼
pyproject.toml (dependencies, tool config)
    │
    ▼
uv (package/venv management)
```

## Consequences

### Benefits

- **Fast iteration**: uv and ruff are significantly faster than traditional Python tools
- **Debuggable tasks**: nox sessions are Python code, not opaque config
- **Standard interface**: `make test` works the same everywhere
- **Modern standards**: pyproject.toml is the Python packaging future
- **CI agnostic**: Makefile provides the abstraction layer per ADR-002
- **Unified linting**: ruff replaces multiple tools (flake8, black, isort) with one

### Costs

- **Tool learning**: Team needs to learn uv, nox, and ruff (though all are well-documented)
- **nox overhead**: More verbose than tox for simple cases
- **Newer tools**: uv and ruff are rapidly maturing but younger than alternatives
- **Makefile quirks**: Make has syntax oddities (tabs, etc.)

### Migration Path

If we later decide to change tools:
- **uv → pip/poetry**: Change noxfile.py installation commands
- **nox → tox**: Rewrite noxfile.py as tox.ini, update Makefile targets
- **Makefile → task.py**: Replace with any script that provides same interface
- **ruff → flake8+black+isort**: Update nox sessions and pyproject.toml config
- **pytest → unittest**: Update test files and nox session commands

The Makefile interface remains stable; only implementations change.

## References

- [ADR-000](./adr-000-architectural-principles.md): Learning-first philosophy
- [ADR-002](./adr-002-ci-cd-agnosticism.md): CI/CD platform agnosticism (this ADR implements)
- [uv documentation](https://docs.astral.sh/uv/)
- [nox documentation](https://nox.thea.codes/)
- [ruff documentation](https://docs.astral.sh/ruff/)
- [pytest documentation](https://docs.pytest.org/)
- [PEP 621](https://peps.python.org/pep-0621/): Project metadata in pyproject.toml
