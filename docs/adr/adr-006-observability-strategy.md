# ADR-006: Observability Strategy

**Status:** Accepted
**Date:** 2025-01-30
**Updated:** 2025-02-01

## Rules

1. **Phoenix Arize for LLM tracing**: Use Phoenix as the observability backend for all agent workflows
2. **OpenTelemetry standard**: All tracing uses OTEL—enables future multi-backend via Collector if needed
3. **Run_id correlation**: All logs and traces must include run_id for end-to-end debugging
4. **Token tracking required**: Every LLM call must log model, tokens_in, tokens_out, and estimated cost
5. **PostgreSQL for production**: Use SQLite for local dev, PostgreSQL (v14+) for deployed environments

## Context

Per [ADR-000](./adr-000-architectural-principles.md), observability is foundational: "If it's not traced, it didn't happen."

We need observability for:

1. **Debugging**: Why did this run produce bad output?
2. **Cost tracking**: How much did this run cost in LLM tokens?
3. **Evaluation**: How do different agent configs compare?
4. **Audit**: What exactly happened in this workflow?

dapr-agents provides built-in support for multiple backends:
- Zipkin (simple distributed tracing)
- Jaeger via OTEL (CNCF project, richer UI)
- Phoenix Arize (LLM-specific: prompts, responses, token analysis)

## Decision

### Start with dapr-agents defaults

Use whatever observability dapr-agents provides out of the box. All options use OpenTelemetry under the hood, so switching backends later is straightforward.

### Backend evaluation

Before committing to a specific backend, run the dapr-agents quickstarts:
- [Zipkin quickstart](https://github.com/dapr/dapr-agents/tree/main/quickstarts/09-agent-observability)
- [OTEL/Jaeger quickstart](https://github.com/dapr/dapr-agents/tree/main/quickstarts/09-agent-observability)
- [Phoenix Arize quickstart](https://github.com/dapr/dapr-agents/tree/main/quickstarts/09-agents-as-activities-observability)

Evaluation criteria:
- Does it show what we need for debugging? (trace through workflow)
- Can we see LLM token usage and costs?
- Is the setup complexity acceptable for local dev?

### Backend choice: Phoenix Arize

After running the dapr-agents quickstarts, **Phoenix Arize** is the chosen backend:

| Backend | Verdict | Notes |
|---------|---------|-------|
| Zipkin | Too basic | General tracing only, no LLM-specific views |
| Jaeger | Good tracing | Better UI than Zipkin, but still generic |
| Phoenix | **Selected** | LLM-native: shows prompts, responses, token counts |

Phoenix provides out-of-the-box visibility into what matters for agent debugging: the actual prompts sent, responses received, and token consumption per call.

#### Phoenix configuration

Phoenix uses environment variables for configuration:

| Variable | Purpose | Default |
|----------|---------|---------|
| `PHOENIX_SQL_DATABASE_URL` | Database connection | SQLite in temp dir |
| `PHOENIX_WORKING_DIR` | SQLite file location | System temp |
| `PHOENIX_COLLECTOR_ENDPOINT` | OTLP endpoint | `localhost:4317` (gRPC) |
| `PHOENIX_DEFAULT_RETENTION_POLICY_DAYS` | Auto-cleanup | 0 (infinite) |

For production, PostgreSQL (v14+) is recommended over SQLite.

### Multi-backend forwarding (future option)

Phoenix is an observability **backend**, not a collector—it receives and stores traces but doesn't forward them elsewhere.

If we later need to persist raw traces AND forward to multiple systems (e.g., Phoenix for LLM analysis + Jaeger for general tracing + cloud vendor for long-term storage), the pattern is:

```
App → OTEL Collector → Phoenix
                    → Jaeger
                    → Cloud vendor
```

The OTEL Collector supports this via pipeline configuration with multiple exporters. This is not needed initially but is a clean upgrade path since everything uses OTLP.

### Structured logging

Regardless of tracing backend, use structured JSON logs with correlation:

```python
logger.info(
    "Agent contribution completed",
    extra={
        "run_id": run_id,
        "phase": "risk-analysis",      # protocol-agnostic (not "hat")
        "role": "critic",              # protocol-agnostic (not "black hat")
        "agent_id": "pessimist-v1",
        "model": "gpt-4o-mini",
        "tokens_in": 450,
        "tokens_out": 230,
    }
)
```

### Cost tracking

Track costs in application code (not dependent on observability backend):

```python
def log_llm_call(run_id: str, model: str, tokens_in: int, tokens_out: int):
    cost = estimate_cost(model, tokens_in, tokens_out)
    logger.info("LLM call", extra={
        "run_id": run_id,
        "model": model,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": cost,
    })
```

## Consequences

### Benefits

- **Low commitment**: Can switch backends as needs evolve
- **Immediate value**: Structured logs work without any backend
- **OTEL foundation**: Industry standard, well-supported by dapr-agents
- **Cost awareness**: Token tracking built into application code

### Costs

- **Deferred decision**: Won't have "the answer" until quickstarts are validated
- **Manual cost tracking**: Must implement token/cost logging ourselves
- **Learning curve**: Will need to learn chosen backend eventually

### Next Steps

1. ~~Run dapr-agents observability quickstarts~~ ✓ Done
2. ~~Pick simplest backend that shows LLM traces clearly~~ ✓ Phoenix selected
3. ~~Update this ADR with specific backend choice~~ ✓ Updated above
4. Configure Phoenix persistence (SQLite for dev, PostgreSQL for prod)
5. Implement structured logging with run_id correlation
6. If multi-backend needed later: add OTEL Collector as intermediary

## References

- [dapr-agents observability quickstart](https://github.com/dapr/dapr-agents/tree/main/quickstarts/09-agents-as-activities-observability)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Phoenix persistence docs](https://docs.arize.com/phoenix/deployment/persistence)
- [Phoenix OTEL setup](https://arize.com/docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-using-phoenix-otel)
- [OTEL Collector architecture](https://opentelemetry.io/docs/collector/architecture/) (for multi-backend fanout)
- [ADR-000](./adr-000-architectural-principles.md): Observable by Default principle
- [ADR-005](./adr-005-dapr-agents-framework.md): dapr-agents as framework
