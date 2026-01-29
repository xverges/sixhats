# ADR-000: Architectural Principles

**Status:** Accepted
**Date:** 2025-01-28

## Context

We are building a multi-agent system to evaluate scenarios using structured thinking protocols. **Six Thinking Hats** is our first implementation, but the architecture should not preclude other cognitive frameworks (SCAMPER, design thinking, lateral thinking, etc.).

### Learning-First Philosophy

This project prioritizes **deep understanding over delivery speed**. We may intentionally build components that exist as libraries when doing so provides learning value. This is not accidental complexity—it's deliberate exploration.

When we "reinvent the wheel," we will:
- Document what we learned from building it
- Note how our approach differs from existing solutions
- Be explicit that we know alternatives exist

This philosophy does not excuse poor engineering. We still aim for clean, testable, well-documented code. We simply optimize for understanding over expedience.

### System Requirements

The system must support:

- Parallel cognitive agents assuming the same role
- Strict separation between orchestration and cognition
- Human-in-the-loop control (human as facilitator/orchestrator)
- Fully automated end-to-end workflows
- Inspectable, replayable reasoning traces
- Quantitative evaluation of thinking quality
- Flexible agent configurations for experimentation

This ADR establishes the foundational principles that guide all subsequent architectural decisions.

## Decision

All architecture decisions must uphold these principles:

### 1. Protocol-Agnostic Core
> Six Thinking Hats is an implementation, not the architecture.

- The orchestration layer works with abstract concepts: **roles**, **phases**, **contributions**, **synthesis**
- Six Thinking Hats maps its vocabulary onto these abstractions (hat → role, round → phase)
- Protocol-specific logic lives in configuration and protocol adapters, not in core orchestration
- Adding a new thinking protocol should not require modifying the orchestrator

### 2. Cognitive Separation
> Agents think. Orchestrators coordinate. Never mix them.

- Agents receive context, produce contributions, return results
- Agents do NOT know the workflow, control flow, or other agents
- The orchestrator manages lifecycle, sequencing, and fan-out/fan-in
- The orchestrator does NOT generate cognitive content

### 3. Observable by Default
> If it's not traced, it didn't happen.

- Every LLM call must produce a trace span
- Every agent contribution must be logged with provenance
- Every state mutation must be recorded
- Observability is not optional—it's built into every component

### 4. Evaluable by Design
> The system must be able to judge its own outputs.

- All reasoning artifacts are structured for automated evaluation
- Every run produces a scoreable workspace
- Agent configurations can be compared quantitatively
- Evaluation is a first-class workflow, not an afterthought

### 5. Append-Only Reasoning Memory
> Never overwrite thinking—only add to it.

- Raw agent contributions are immutable
- Synthesis builds on top of raw, doesn't replace it
- Decisions reference their inputs
- Full history is always available for replay and audit

### 6. Human Sovereignty
> Humans decide. Agents advise.

- Humans can pause any workflow
- Humans can override any synthesis
- Humans can inject new framing or constraints
- The system presents options, not conclusions (unless configured otherwise)

### 7. Replaceable Intelligence
> No vendor lock-in for the thinking parts.

- LLM providers are abstracted behind interfaces
- Agent prompts are configuration, not code
- Models can be swapped per agent type
- Cost/quality tradeoffs are explicit

### 8. Fail Gracefully
> Partial thinking is better than no thinking.

- Agent failures don't crash the workflow
- Timeouts produce partial results, not errors
- The system degrades gracefully under load
- All failures are logged with context for debugging

## Consequences

### Benefits
- **Debuggable**: Full traces mean we can understand what happened
- **Evaluable**: Structured artifacts enable automated quality assessment
- **Flexible**: Agent configurations can be experimented with safely
- **Auditable**: Append-only memory creates complete reasoning trails
- **Trustworthy**: Human sovereignty builds trust in the system
- **Extensible**: Protocol-agnostic core enables experimentation with other thinking frameworks
- **Educational**: Learning-first approach builds deep understanding of multi-agent systems

### Costs
- **More complexity**: Separation of concerns means more components
- **Storage overhead**: Append-only memory grows unboundedly (need retention policy)
- **Instrumentation burden**: Every component must emit traces
- **Testing complexity**: Distributed system requires integration tests
- **Slower initial delivery**: Learning-first means building things that could be imported
- **Abstraction overhead**: Protocol-agnostic design requires mapping layers

## References

- [ADR-001](./adr-001-coding-assistant-agnosticism.md): Coding assistant agnosticism
- [ADR-002](./adr-002-ci-cd-agnosticism.md): CI/CD platform agnosticism
- [ADR-003](./adr-003-python-tooling.md): Python tooling
- [ADR-004](./adr-004-dapr-agents-framework.md): Framework choice
- [ADR-005](./adr-005-observability-strategy.md): Observability implementation
- [ADR-006](./adr-006-evaluation-framework.md): Evaluation approach
