"""Nox sessions for sixhats development tasks.

See ADR-003 (Python Tooling) for the layered architecture:
Makefile → nox → uv
"""

import nox

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True


@nox.session
def format(session: nox.Session) -> None:
    """Format code with ruff."""
    session.install("ruff")
    session.run("ruff", "format", ".")


@nox.session
def lint(session: nox.Session) -> None:
    """Run the linter."""
    session.install("ruff")
    session.run("ruff", "check", ".")


@nox.session
def test(session: nox.Session) -> None:
    """Run the test suite."""
    session.install("-e", ".[dev]")
    session.run("pytest", *session.posargs)


@nox.session
def typecheck(session: nox.Session) -> None:
    """Run pyright type checker."""
    session.install("-e", ".[dev]")
    session.run("pyright", "src/", *session.posargs)
