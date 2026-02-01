# ADR-010: Workspace Schema Design

**Status:** Accepted
**Date:** 2025-02-01

## Rules

<!-- AI: This section contains actionable constraints. Read this first. -->

1. **Append-only contributions**: Agents append to `raw[]`, never modify existing entries or synthesis
2. **Synthesis references sources**: Aggregators set synthesis with `derived_from` listing source contribution_ids
3. **Hat structure**: Each hat maintains separate `raw[]` (immutable) and `synthesis` (aggregated output)
4. **Provenance tracking**: Every contribution must include agent info, timestamps, and token counts
5. **Artifact traceability**: Decisions and action items must include `based_on` references to source contributions/syntheses
6. **State store key format**: Use `workspace:{run_id}` as key pattern in Dapr state store
7. **Protocol versioning**: Include version in `run.protocol` field (e.g., `six_thinking_hats:v1`) for migrations

## Context

Per [ADR-000](./adr-000-architectural-principles.md):
- "Explicit cognition artifacts (raw → synthesis → decisions)"
- "Append-only reasoning memory"

> **Known deviation**: ADR-000 requires a protocol-agnostic core (`hat → role`, `round → phase`). This schema is Six Hats-specific. We defer abstraction until we have concrete experience with what a second protocol (SCAMPER, design thinking) would need. Revisit after the first end-to-end workflow is complete.

We need a schema that:
1. Captures all reasoning artifacts
2. Preserves provenance (who said what, when)
3. Separates raw contributions from synthesized knowledge
4. Supports evaluation and replay
5. Is queryable and inspectable

## Decision

### Core Schema Structure

```
Workspace
├── run (identity, timing, config)
├── scenario (problem framing)
├── hats
│   ├── white (facts)
│   │   ├── raw[] (immutable contributions)
│   │   └── synthesis (aggregated output)
│   ├── red (emotions)
│   ├── black (risks)
│   ├── yellow (benefits)
│   ├── green (ideas)
│   └── blue (process)
├── artifacts (cross-hat outputs)
│   ├── decisions[]
│   ├── action_items[]
│   └── open_questions[]
└── audit (events, metrics)
```

### Pydantic Models

**Source of truth:** [`src/schemas/workspace.py`](../../src/schemas/workspace.py)

Key models:
- `Workspace` — root container with run, scenario, hats, artifacts, audit
- `HatState` — contains `raw: list[Contribution]` and `synthesis: Optional[Synthesis]`
- `Contribution` — immutable agent output with provenance
- `Synthesis` — aggregated output with `derived_from` references
- `Decision`, `ActionItem`, `OpenQuestion` — cross-hat artifacts

### Access Patterns

#### Agents Write:
```python
# Agents append to raw[], never modify synthesis
workspace.hats[HatType.BLACK].raw.append(contribution)
```

#### Aggregators Write:
```python
# Aggregators set synthesis, referencing raw contributions
workspace.hats[HatType.BLACK].synthesis = Synthesis(
    synthesis_id=str(uuid4()),
    hat=HatType.BLACK,
    summary="...",
    key_points=["..."],
    derived_from=[c.contribution_id for c in contributions]
)
```

#### Orchestrator Writes:
```python
# Orchestrator manages run state and audit
workspace.run.status = RunStatus.RUNNING
workspace.audit.events.append(AuditEvent(
    event_id=str(uuid4()),
    event_type="HAT_STARTED",
    hat=HatType.BLACK,
    actor="orchestrator"
))
```

#### Human Writes:
```python
# Human can write to blue hat and artifacts
workspace.hats[HatType.BLUE].raw.append(Contribution(
    agent=AgentInfo(agent_id="human", persona="facilitator", ...),
    content="I think we should focus on...",
    ...
))
workspace.artifacts.decisions.append(Decision(
    statement="Proceed with pilot",
    made_by="human",
    ...
))
```

### Storage

Store as JSON in Dapr state store:

```python
from dapr.clients import DaprClient

async def save_workspace(workspace: Workspace):
    async with DaprClient() as client:
        await client.save_state(
            store_name="workspacestore",
            key=f"workspace:{workspace.run.run_id}",
            value=workspace.model_dump_json()
        )

async def load_workspace(run_id: str) -> Workspace:
    async with DaprClient() as client:
        state = await client.get_state(
            store_name="workspacestore",
            key=f"workspace:{run_id}"
        )
        return Workspace.model_validate_json(state.data)
```

### Versioning

Schema version in protocol field:
```python
run.protocol = "six_thinking_hats:v1"
```

Future migrations:
```python
def migrate_workspace(workspace_dict: dict) -> Workspace:
    version = workspace_dict.get("run", {}).get("protocol", "v0")
    if version == "six_thinking_hats:v0":
        workspace_dict = migrate_v0_to_v1(workspace_dict)
    return Workspace.model_validate(workspace_dict)
```

## Consequences

### Benefits

- **Type safety**: Pydantic validates all data
- **Provenance**: Every artifact tracks its origin
- **Queryable**: Can filter/search contributions, syntheses
- **Replayable**: Full history preserved
- **Evaluable**: Structured data enables automated scoring

### Costs

- **Storage size**: Append-only grows unboundedly (need retention)
- **Schema evolution**: Changes require migration
- **Serialization overhead**: JSON not most compact

### Implementation Notes

1. Start with JSON storage (simple, debuggable)
2. Consider moving to vector store for semantic search later
3. Add retention policy when storage becomes an issue
4. Export to Parquet for analytics workloads

## References

- [ADR-000](./adr-000-architectural-principles.md): Append-only memory principle
- [ADR-008](./adr-008-evaluation-framework.md): Evaluation uses this schema
- [Pydantic docs](https://docs.pydantic.dev/)
