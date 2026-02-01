# ADR-007: LLM Provider Strategy

**Status:** Accepted
**Date:** 2025-02-01

## Rules

1. **Provider abstraction required**: All LLM calls must use dapr-agents `ChatClient`—no direct provider SDK calls
2. **Model selection by task**: Use cheaper models (GPT-4o-mini/Haiku) for agent contributions, quality models (GPT-4o/Sonnet) for aggregation and synthesis
3. **Cost tracking**: Track and log estimated costs per run for budget management
4. **Rate limit handling**: Use jitter for parallel calls and Dapr resiliency policies for retries
5. **Dapr handles recovery**: Rely on Dapr's built-in resiliency policies for failure recovery—no custom fallback chains

## Context

Per [ADR-000](./adr-000-architectural-principles.md), we need "Replaceable Intelligence" with no vendor lock-in.

The system makes many LLM calls:
- 3-5 parallel agents per hat × 6 hats = 18-30 agent calls
- 6 aggregation calls
- 1 final synthesis
- Plus evaluation calls

This adds up. We need a strategy for:
1. Abstracting providers
2. Optimizing cost
3. Handling rate limits
4. Selecting models per task

## Decision

### Provider Abstraction

Use dapr-agents' `ChatClient` which provides provider abstraction:

```python
from dapr_agents.llm import ChatClient

# Provider configured via environment/config, not code
client = ChatClient()  # Uses DAPR_LLM_PROVIDER env var

# Same interface regardless of provider
response = await client.chat(messages=[
    {"role": "system", "content": "You are a risk analyst..."},
    {"role": "user", "content": scenario}
])
```

Supported providers (via dapr-agents):
- OpenAI (GPT-4, GPT-4o, GPT-4o-mini)
- Anthropic (Claude 3.5, Claude 3)
- Mistral (Mistral Large, Mistral Small)
- Azure OpenAI
- Local models via Ollama

### Model Selection by Task

Not all tasks need the most expensive model:

| Task | Recommended Model | Rationale |
|------|-------------------|-----------|
| Parallel agent contributions | Claude Haiku / Mistral Small / GPT-4o-mini | High volume, simpler task |
| Aggregation/Synthesis | Claude Sonnet / Mistral Large / GPT-4o | Needs reasoning quality |
| Blue Hat (final) | Claude Sonnet / Mistral Large / GPT-4o | Critical output |
| LLM-as-Judge (eval) | Claude Sonnet / Mistral Large / GPT-4o | Needs calibrated judgment |

Configuration:

```yaml
# config/models.yaml
models:
  agent_contribution:
    provider: anthropic
    model: claude-3-haiku
    temperature: 0.7
    max_tokens: 1000

  aggregation:
    provider: anthropic
    model: claude-3-5-sonnet
    temperature: 0.3
    max_tokens: 2000

  synthesis:
    provider: anthropic
    model: claude-3-5-sonnet
    temperature: 0.3
    max_tokens: 3000

  evaluation:
    provider: anthropic
    model: claude-3-5-sonnet
    temperature: 0.0  # Deterministic for consistency
    max_tokens: 500
```

### Cost Tracking

Track and report costs per run:

```python
# Approximate costs per 1K tokens (as of Jan 2025)
COSTS = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "mistral-large": {"input": 0.002, "output": 0.006},
    "mistral-small": {"input": 0.0002, "output": 0.0006},
}

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    costs = COSTS.get(model, {"input": 0, "output": 0})
    return (input_tokens / 1000 * costs["input"] +
            output_tokens / 1000 * costs["output"])
```

Estimated cost per full Six Hats run:

| Configuration | Est. Cost | Notes |
|---------------|-----------|-------|
| All Mistral Small | ~$0.04 | Fast, cheap, lower quality |
| All GPT-4o-mini | ~$0.05 | Fast, cheap, lower quality |
| Mixed (small + large) | ~$0.12 | Balanced |
| Mixed (mini + 4o) | ~$0.15 | Balanced |
| All Mistral Large | ~$0.25 | High quality, good value |
| All GPT-4o | ~$0.40 | High quality, slower |
| All Claude Sonnet | ~$0.50 | Highest quality |

### Rate Limit Handling

dapr-agents provides resilience policies. Configure:

```yaml
# dapr/components/resiliency.yaml
policies:
  llm-retry:
    timeout: 30s
    retries:
      policy: constant
      maxRetries: 3
      duration: 5s
    circuitBreaker:
      maxRequests: 10
      timeout: 60s
      trip: consecutiveFailures >= 5
```

For parallel calls, add jitter to avoid thundering herd:

```python
async def call_with_jitter(agent, scenario):
    await asyncio.sleep(random.uniform(0, 0.5))  # 0-500ms jitter
    return await agent.run(scenario)
```

## Consequences

### Benefits

- **No lock-in**: Can switch providers without code changes
- **Cost optimization**: Use cheap models where appropriate
- **Resilience**: Dapr's built-in resiliency handles transient failures
- **Transparency**: Cost tracking enables budget management

### Costs

- **Configuration complexity**: More settings to manage
- **Quality variance**: Cheap models may produce lower quality
- **Testing burden**: Should test with each provider
- **Cost estimation drift**: Prices change, estimates become stale

### Implementation Notes

1. Start with Anthropic as primary provider
2. Consider Ollama for local development (free, fast iteration)
3. Update cost estimates quarterly

## References

- [dapr-agents LLM quickstart](https://github.com/dapr/dapr-agents/tree/main/quickstarts/02-llm-dapr-chat-client)
- [Anthropic pricing](https://www.anthropic.com/pricing)
- [Mistral pricing](https://mistral.ai/products/la-plateforme#pricing)
- [OpenAI pricing](https://openai.com/pricing)
- [ADR-000](./adr-000-architectural-principles.md): Replaceable Intelligence principle
