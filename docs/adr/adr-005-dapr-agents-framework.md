# ADR-005: Use dapr-agents as Agent Framework

**Status:** Accepted
**Date:** 2025-01-28

## Rules

1. **Single framework**: All agent orchestration uses dapr-agents—no mixing frameworks
2. **Dapr required**: Local dev and production require Dapr runtime (CLI + sidecar)
3. **Validate patterns early**: Test workflow patterns (especially fan-out/fan-in) before building full implementation

## Context

We need a framework that provides:

- Agent abstractions with tool calling
- Workflow orchestration with durable execution
- State management for workspace persistence
- Parallel execution with fan-out/fan-in
- Pub/sub messaging for agent coordination
- Built-in observability hooks
- Local development to production portability

Options considered:

1. **Raw Dapr** - Use Dapr primitives directly (workflows, state, service invocation)
2. **dapr-agents** - Purpose-built agent framework on top of Dapr
3. **LangGraph** - LangChain's agent orchestration framework
4. **CrewAI** - Multi-agent orchestration framework
5. **Custom** - Build our own agent framework

## Decision

Use **dapr-agents** as the agent framework.

dapr-agents provides:

| Capability | dapr-agents Feature |
|------------|---------------------|
| Agent abstraction | `Agent` class with ReAct pattern |
| Tool calling | Built-in function calling support |
| Workflow orchestration | `@workflow` with `@agent_activity` decorator |
| Parallel execution | `ctx.all()` for fan-out, automatic fan-in |
| State management | Dapr state store integration |
| Actor model | Virtual actors for stateful agents |
| Observability | Native Zipkin, Jaeger, Phoenix Arize support |
| Human-in-the-loop | Workflow pause/resume with external events |

### Why not alternatives?

- **Raw Dapr**: Would require building agent abstractions ourselves. dapr-agents already did this well.
- **LangGraph**: Tied to LangChain ecosystem, less control over infrastructure
- **CrewAI**: Simpler but less control over orchestration patterns
- **Custom**: No good reason to rebuild what dapr-agents provides

## Consequences

### Benefits

- **Production-ready**: Built for scale (thousands of agents on single core)
- **Durable execution**: Workflows survive failures and restarts
- **Observability built-in**: Tracing works out of the box
- **Active development**: Part of CNCF Dapr project, well-maintained
- **Portable**: Same code runs locally, on edge, or in Kubernetes
- **Language-agnostic future**: Can add agents in other languages later

### Costs

- **Learning curve**: Must learn Dapr concepts (sidecars, components, workflows)
- **Debugging complexity**: Some debugging happens in Dapr sidecars
- **Dependency**: Tied to Dapr ecosystem (acceptable given benefits)
- **Python-first**: Currently best support is Python (fine for us)

### Technical Implications

1. **Local development** requires Dapr CLI and sidecar running
2. **Testing** requires either Dapr test containers or mocking
3. **Deployment** needs Dapr-enabled Kubernetes or self-hosted Dapr
4. **Agent code** uses dapr-agents patterns:

```python
from dapr_agents import Agent, tool
from dapr_agents.workflow import workflow, agent_activity

@tool
def analyze_risk(scenario: str) -> str:
    """Analyze risks in the given scenario."""
    # Tool implementation
    pass

black_hat_agent = Agent(
    name="black-hat-pessimist",
    instructions="You are a cautious risk analyst...",
    tools=[analyze_risk]
)

@agent_activity
async def black_hat_contribution(ctx, scenario: str, persona: str):
    agent = get_agent_for_persona("black", persona)
    return await agent.run(scenario)

@workflow
async def six_hats_workflow(ctx, scenario: Scenario):
    # Fan-out to parallel agents
    contributions = await ctx.all([
        black_hat_contribution(ctx, scenario, persona)
        for persona in ["pessimist", "regulator", "skeptic"]
    ])
    # Continue workflow...
```

## References

- [dapr-agents GitHub](https://github.com/dapr/dapr-agents)
- [dapr-agents quickstarts](https://github.com/dapr/dapr-agents/tree/main/quickstarts)
- [ADR-000](./adr-000-architectural-principles.md): Architectural principles this implements
