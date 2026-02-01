# ADR-009: Failure Handling Strategy

**Status:** Accepted
**Date:** 2025-02-01

## Rules

<!-- AI: This section contains actionable constraints. Read this first. -->

1. **Retry transient failures**: Use exponential backoff, max 3 attempts, 2-30s intervals
2. **Continue on partial agent failures**: If at least one agent succeeds, proceed with partial results
3. **Fallback on aggregation failure**: Return raw contributions with confidence=0.0 synthesis
4. **Checkpoint after each activity**: Leverage dapr-agents workflow durability for resume
5. **Pause on critical failures**: Set status to WAITING_FOR_HUMAN, await external event
6. **Dead letter unrecoverable workspaces**: Preserve failed state with full context for post-mortem
7. **Alert on critical failures**: Publish to alerts topic with severity, run_id, and error

## Context

Per [ADR-000](./adr-000-architectural-principles.md): "Fail Gracefully - Partial thinking is better than no thinking."

In a multi-agent workflow, many things can fail:
- LLM API timeouts or rate limits
- Individual agent producing invalid output
- Aggregator failing to synthesize
- State store unavailable
- Workflow interrupted mid-execution

We need a strategy that:
1. Doesn't lose completed work
2. Allows resumption from failure point
3. Provides partial results when possible
4. Logs failures for debugging

## Decision

### Failure Categories

| Category | Example | Strategy |
|----------|---------|----------|
| Transient | Rate limit, timeout | Retry with backoff |
| Agent failure | Bad output, parse error | Skip agent, continue with others |
| Aggregation failure | Synthesis fails | Return raw contributions |
| Critical | State store down | Pause workflow, alert |
| Corruption | Invalid workspace state | Fail run, preserve last good state |

### Retry Policy

For transient failures, use exponential backoff:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30)
)
async def call_agent(agent, scenario):
    return await agent.run(scenario)
```

Dapr also provides built-in resiliency:

```yaml
# dapr/components/resiliency.yaml
policies:
  agent-retry:
    timeout: 60s
    retries:
      policy: exponential
      maxRetries: 3
      maxInterval: 30s
```

### Partial Results

When some agents fail, continue with successful ones:

```python
async def run_hat_phase(hat: HatType, personas: list[str]) -> HatState:
    tasks = [call_agent_safe(hat, p) for p in personas]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    contributions = []
    failures = []

    for persona, result in zip(personas, results):
        if isinstance(result, Exception):
            failures.append({"persona": persona, "error": str(result)})
            log_agent_failure(hat, persona, result)
        else:
            contributions.append(result)

    # Record failures in audit
    if failures:
        workspace.audit.events.append(AuditEvent(
            event_type="AGENT_FAILURES",
            hat=hat,
            data={"failures": failures, "success_count": len(contributions)}
        ))

    # Continue if we have at least one contribution
    if contributions:
        return HatState(raw=contributions)
    else:
        raise AllAgentsFailedError(f"All agents failed for {hat}")
```

### Aggregation Fallback

If aggregation fails, return raw contributions:

```python
async def aggregate_with_fallback(hat: HatType, contributions: list[Contribution]) -> HatState:
    try:
        synthesis = await aggregate(hat, contributions)
        return HatState(raw=contributions, synthesis=synthesis)
    except AggregationError as e:
        log_aggregation_failure(hat, e)

        # Create a minimal "fallback synthesis"
        fallback = Synthesis(
            synthesis_id=str(uuid4()),
            hat=hat,
            summary=f"[Aggregation failed - showing {len(contributions)} raw contributions]",
            key_points=[c.content[:200] for c in contributions[:5]],
            confidence=0.0,
            derived_from=[c.contribution_id for c in contributions]
        )

        workspace.audit.events.append(AuditEvent(
            event_type="AGGREGATION_FALLBACK",
            hat=hat,
            data={"error": str(e)}
        ))

        return HatState(raw=contributions, synthesis=fallback)
```

### Workflow Checkpointing

dapr-agents workflows are durable by default. State is checkpointed after each activity:

```python
@workflow
async def six_hats_workflow(ctx, scenario: Scenario) -> Workspace:
    workspace = await init_workspace_activity(ctx, scenario)
    # ↑ Checkpoint saved

    for hat in [HatType.WHITE, HatType.BLACK, HatType.GREEN]:
        contributions = await run_hat_activity(ctx, hat, workspace)
        # ↑ Checkpoint saved after each hat

        workspace = await aggregate_activity(ctx, hat, contributions, workspace)
        # ↑ Checkpoint saved

    return workspace
```

If workflow crashes, it resumes from last checkpoint, not from beginning.

### Human Intervention Points

When critical failures occur, pause for human:

```python
async def handle_critical_failure(ctx, error: Exception, workspace: Workspace):
    workspace.run.status = RunStatus.WAITING_FOR_HUMAN
    workspace.audit.events.append(AuditEvent(
        event_type="CRITICAL_FAILURE",
        data={"error": str(error), "error_type": type(error).__name__}
    ))

    await save_workspace(workspace)

    # Wait for human to resolve and signal continuation
    human_decision = await ctx.wait_for_external_event("human_intervention")

    if human_decision.action == "retry":
        return "retry"
    elif human_decision.action == "skip":
        return "skip"
    else:
        raise WorkflowAbortedError("Human aborted workflow")
```

### Dead Letter Queue

For unrecoverable failures, preserve the workspace for analysis:

```python
async def dead_letter_workspace(workspace: Workspace, error: Exception):
    """Store failed workspace for post-mortem analysis."""
    await save_state(
        store_name="deadletter",
        key=f"failed:{workspace.run.run_id}:{datetime.utcnow().isoformat()}",
        value={
            "workspace": workspace.model_dump(),
            "error": str(error),
            "error_type": type(error).__name__,
            "traceback": traceback.format_exc()
        }
    )
```

### Alerting

Critical failures should alert:

```python
async def alert_on_failure(workspace: Workspace, error: Exception):
    if is_critical(error):
        await publish_event(
            topic="alerts",
            data={
                "severity": "critical",
                "run_id": workspace.run.run_id,
                "error": str(error),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

## Consequences

### Benefits

- **No lost work**: Checkpointing preserves progress
- **Graceful degradation**: Partial results better than nothing
- **Debuggable**: All failures logged with context
- **Resumable**: Can continue from failure point
- **Observable**: Failure metrics enable monitoring

### Costs

- **Complexity**: More code paths to handle
- **Testing burden**: Must test failure scenarios
- **Partial quality**: Degraded results may be confusing
- **Alert fatigue**: Need good alert thresholds

### Open Questions

1. How many agent failures before aborting a hat phase?
2. Should fallback synthesis be visually distinct in UI?
3. How long to retain dead-lettered workspaces?
4. Who receives critical alerts?

## References

- [ADR-000](./adr-000-architectural-principles.md): Fail Gracefully principle
- [ADR-006](./adr-006-observability-strategy.md): Failure logging
- [dapr-agents resiliency](https://github.com/dapr/dapr-agents)
- [Dapr resiliency policies](https://docs.dapr.io/operations/resiliency/)
