"""Nox sessions for sixhats development tasks.

See ADR-003 (Python Tooling) for the layered architecture:
Makefile → nox → uv

Uses nox-uv to install dependencies from uv's lockfile and dependency groups.
"""

import nox
from nox_uv import session

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True


@session(uv_only_groups=["dev"])
def format(session: nox.Session) -> None:
    """Format code with ruff."""
    session.run("ruff", "format", ".")


@session(uv_only_groups=["dev"])
def lint(session: nox.Session) -> None:
    """Run the linter."""
    session.run("ruff", "check", ".")


@session(uv_groups=["dev"])
def test(session: nox.Session) -> None:
    """Run the test suite."""
    session.run("pytest", *session.posargs)


@session(uv_groups=["dev"])
def typecheck(session: nox.Session) -> None:
    """Run pyright type checker."""
    session.run("pyright", "src/", *session.posargs)
