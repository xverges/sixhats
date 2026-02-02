"""
Observability and tracing for Six Thinking Hats.

Implements ADR-006: Phoenix Arize backend with OpenTelemetry standard.
"""

from src.observability.tracing import configure_tracing, get_tracer

__all__ = ["configure_tracing", "get_tracer"]
