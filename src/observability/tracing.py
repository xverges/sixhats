"""
OpenTelemetry tracing configuration for Phoenix Arize.

Per ADR-006:
- Phoenix Arize for LLM-specific tracing
- OpenTelemetry standard for all tracing
- run_id correlation across all logs and traces
- Token tracking required for all LLM calls

Environment variables:
- PHOENIX_COLLECTOR_ENDPOINT: Phoenix OTLP endpoint (default: http://localhost:6006/v1/traces)
- OTEL_SERVICE_NAME: Service name for traces (default: sixhats)
"""

import os
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

_tracer_provider: TracerProvider | None = None


def configure_tracing(
    service_name: str = "sixhats",
    phoenix_endpoint: str | None = None,
) -> TracerProvider:
    """
    Configure OpenTelemetry tracing with Phoenix Arize backend.

    Args:
        service_name: Name of the service for traces
        phoenix_endpoint: Phoenix OTLP endpoint URL

    Returns:
        Configured TracerProvider
    """
    global _tracer_provider

    if _tracer_provider is not None:
        return _tracer_provider

    # Get endpoint from env or parameter
    endpoint = phoenix_endpoint or os.getenv(
        "PHOENIX_COLLECTOR_ENDPOINT",
        "http://localhost:6006/v1/traces",
    )

    # Create resource with service info
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": "0.1.0",
        }
    )

    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)

    # Add Phoenix OTLP exporter
    otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
    span_processor = BatchSpanProcessor(otlp_exporter)
    _tracer_provider.add_span_processor(span_processor)

    # Set as global provider
    trace.set_tracer_provider(_tracer_provider)

    return _tracer_provider


def get_tracer(name: str = "sixhats") -> trace.Tracer:
    """
    Get a tracer instance.

    Args:
        name: Name for the tracer (typically module name)

    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)


@contextmanager
def trace_llm_call(
    tracer: trace.Tracer,
    operation: str,
    run_id: str,
    hat_type: str | None = None,
    agent_id: str | None = None,
    model: str | None = None,
):
    """
    Context manager for tracing LLM calls with run_id correlation.

    Usage:
        with trace_llm_call(tracer, "analyze", run_id, hat_type="black") as span:
            response = await llm.generate(...)
            span.set_attribute("tokens.input", response.usage.prompt_tokens)
            span.set_attribute("tokens.output", response.usage.completion_tokens)

    Args:
        tracer: Tracer instance
        operation: Name of the operation (e.g., "analyze", "synthesize")
        run_id: Unique run identifier for correlation
        hat_type: Optional hat type (white, red, black, yellow, green, blue)
        agent_id: Optional agent identifier
        model: Optional model name
    """
    with tracer.start_as_current_span(operation) as span:
        # Set correlation attributes per ADR-006
        span.set_attribute("run_id", run_id)

        if hat_type:
            span.set_attribute("hat.type", hat_type)
        if agent_id:
            span.set_attribute("agent.id", agent_id)
        if model:
            span.set_attribute("llm.model", model)

        yield span


def record_token_usage(
    span: trace.Span,
    tokens_in: int,
    tokens_out: int,
    latency_ms: int,
    cost_usd: float | None = None,
) -> None:
    """
    Record token usage and cost on a span.

    Per ADR-006: Token tracking required for all LLM calls.

    Args:
        span: Active span to record attributes on
        tokens_in: Number of input tokens
        tokens_out: Number of output tokens
        latency_ms: Latency in milliseconds
        cost_usd: Optional estimated cost in USD
    """
    span.set_attribute("llm.tokens.input", tokens_in)
    span.set_attribute("llm.tokens.output", tokens_out)
    span.set_attribute("llm.tokens.total", tokens_in + tokens_out)
    span.set_attribute("llm.latency_ms", latency_ms)

    if cost_usd is not None:
        span.set_attribute("llm.cost_usd", cost_usd)
