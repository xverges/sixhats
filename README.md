# Six Thinking Hats - Multi-Agent Evaluation System

A multi-agent system for evaluating scenarios using Edward de Bono's Six Thinking Hats framework, built on [dapr-agents](https://github.com/dapr/dapr-agents).

## Overview

This system orchestrates multiple AI agents to analyze scenarios from six perspectives:

| Hat | Color | Thinking Style |
|-----|-------|----------------|
| White | ⚪ | Facts, data, information |
| Red | 🔴 | Emotions, intuition, gut feelings |
| Black | ⚫ | Caution, risks, problems |
| Yellow | 🟡 | Benefits, optimism, value |
| Green | 🟢 | Creativity, alternatives, new ideas |
| Blue | 🔵 | Process control, synthesis, decisions |

### Key Features

- **Parallel agents per hat**: Multiple personas contribute in parallel
- **Structured synthesis**: Raw contributions → aggregated insights → decisions
- **Human-in-the-loop**: Act as Blue Hat, or run fully automated
- **Observable**: Full tracing with Phoenix Arize
- **Evaluable**: Automated quality scoring and config comparison

## Project Status

🚧 **In Development** - Phase 2 in progress

**Completed:**
- ✅ Workspace schema with append-only contributions (ADR-010)
- ✅ Black Hat agent implementation with LLM integration
- ✅ Dapr integration for LLM calls via sidecar
- ✅ End-to-end demo working (`examples/black_hat_demo.py`)
- ✅ Phoenix Arize tracing infrastructure (ADR-006)

**Next:**
- Evaluation framework (LLM-as-judge scoring)
- Token tracking in agent spans
- Fan-out to multiple personas per hat

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Orchestrator                            │
│                  (Dapr Workflow)                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │ Agent 1 │      │ Agent 2 │      │ Agent 3 │
   │(persona)│      │(persona)│      │(persona)│
   └────┬────┘      └────┬────┘      └────┬────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ Aggregator  │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │  Workspace  │
                  │   (State)   │
                  └─────────────┘
```

See [Architecture Decision Records](./docs/adr/) for detailed design decisions.

## Quick Start

### Prerequisites

- Python 3.11+
- [Dapr CLI](https://docs.dapr.io/getting-started/install-dapr-cli/)
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key (or other LLM provider)

### Installation

```bash
# Clone and enter the repo
cd sixhats

# Install dependencies
uv sync

# Initialize Dapr
dapr init

# Create secrets file with your API key
echo '{"openai-api-key": "sk-proj-your-key"}' > ../secrets.json
```

### Running the Black Hat Demo

```bash
# Start Phoenix Arize for observability (optional)
uv run phoenix serve

# Run the Black Hat agent demo via Dapr
dapr run --app-id black-hat-demo --resources-path ./components -- \
    uv run python examples/black_hat_demo.py
```

The demo:
1. Creates a scenario (Zero Trust Security Implementation)
2. Runs the Black Hat agent to identify risks
3. Displays the workspace with contribution and audit trail
4. Traces are visible in Phoenix at http://localhost:6006

## Project Structure

```
sixhats/
├── docs/
│   └── adr/                 # Architecture Decision Records
├── src/
│   ├── agents/              # Hat agent implementations
│   │   ├── base.py          # Base agent class
│   │   └── black_hat.py     # Black Hat (risks/problems)
│   ├── schemas/             # Pydantic models
│   │   └── workspace.py     # Workspace, Contribution, Audit
│   ├── observability/       # Tracing configuration
│   │   └── tracing.py       # Phoenix/OTEL setup
│   ├── services/            # Business logic services
│   ├── workflows/           # Dapr workflow definitions
│   └── evals/               # Evaluation framework
├── components/              # Dapr component configurations
├── examples/                # Runnable demos
│   └── black_hat_demo.py    # End-to-end Black Hat demo
├── tests/                   # Test suite
└── scripts/                 # Dev utilities
```

## Architecture Decision Records

See [docs/adr/](./docs/adr/) for all architectural decisions. Run `uv run scripts/adr-list.py` to list accepted ADRs with their rules.

## Action Plan

### Phase 1: Foundation ✅
- [x] Set up local Dapr environment
- [x] Define workspace schema (ADR-010)
- [x] Establish observability strategy (ADR-006)

### Phase 2: Single Hat Prototype 🔄
- [x] Implement Black Hat agent
- [x] Basic workspace with contributions
- [x] End-to-end demo with real LLM
- [ ] Fan-out to 3 personas
- [ ] Aggregator for synthesis

### Phase 3: Evaluation ⬜
- [ ] Structural validation (schema conformance)
- [ ] LLM-as-judge scoring for hat outputs
- [ ] Benchmark scenarios with expected themes

### Phase 4: Observability 🔄
- [x] OpenTelemetry tracing setup
- [x] Phoenix Arize integration
- [ ] Token tracking in agent spans
- [ ] Cost estimation per run

### Phase 5: Full Workflow ⬜
- [ ] All 6 hats implemented
- [ ] Human-in-the-loop pause/resume
- [ ] End-to-end orchestrated run

### Phase 6: Polish ⬜
- [ ] Documentation
- [ ] Demo video
- [ ] Blog post

## Learning Goals

This project demonstrates:

- **Multi-agent orchestration** with dapr-agents
- **Distributed systems patterns** (scatter-gather, saga, actor model)
- **LLM application observability** (tracing, metrics, cost tracking)
- **Evaluation frameworks** for AI systems
- **Production-grade architecture** (failure handling, state management)

## References

- [dapr-agents](https://github.com/dapr/dapr-agents) - The underlying framework
- [Six Thinking Hats](https://en.wikipedia.org/wiki/Six_Thinking_Hats) - The methodology
- [Dapr](https://dapr.io/) - Distributed application runtime

## License

MIT
