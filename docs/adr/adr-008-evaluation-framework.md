# ADR-008: Evaluation Framework

**Status:** Accepted
**Date:** 2025-02-01

## Rules

<!-- AI: This section contains actionable constraints. Read this first. -->

1. **Three-level evaluation**: Evaluate at hat-level (quality criteria per hat), synthesis-level (coverage, accuracy), and run-level (completeness, actionability)
2. **LLM-as-Judge for scoring**: Use a separate LLM to score outputs against defined criteria (1-5 scale)
3. **Structural validation required**: Every run must pass schema conformance and completeness checks before quality scoring
4. **Diversity measurement**: Track diversity of parallel agent outputs using embedding distances
5. **Benchmark scenarios**: Maintain a set of versioned test scenarios with expected themes for regression detection
6. **Results linked to runs**: Store all evaluation results with run_id for comparison across configurations

## Context

Per [ADR-000](./adr-000-architectural-principles.md), the system must be "Evaluable by Design." We need to answer:

1. What makes a "good" Six Thinking Hats run?
2. How do we measure agent quality?
3. How do we compare different configurations?
4. How do we detect regressions?

Without evaluation, we're just generating text and hoping it's useful.

## Decision

### Evaluation Dimensions

We evaluate at three levels:

#### 1. Hat-Level Quality

Each hat has specific quality criteria:

| Hat | Quality Criteria |
|-----|------------------|
| White | Factual accuracy, completeness, identifies unknowns |
| Red | Authentic emotional range, gut reactions captured |
| Black | Risk coverage, severity calibration, no false positives |
| Yellow | Benefit identification, realistic optimism |
| Green | Novelty, feasibility, diversity of ideas |
| Blue | Coherent synthesis, actionable next steps |

#### 2. Synthesis Quality

How well does the aggregator compress parallel contributions?

- **Coverage**: Are all key points from inputs represented?
- **Accuracy**: Does synthesis faithfully reflect inputs?
- **Contradiction handling**: Are disagreements surfaced?
- **Conciseness**: Is redundancy eliminated?

#### 3. Run-Level Quality

Does the full workflow produce useful output?

- **Completeness**: Did all hats execute?
- **Coherence**: Do hat outputs build on each other?
- **Actionability**: Does final output enable decisions?
- **Balance**: Are all perspectives fairly represented?

### Evaluation Methods

#### Method 1: LLM-as-Judge (Automated)

Use a separate LLM to score outputs:

```python
async def eval_synthesis(raw_inputs: list[str], synthesis: str) -> SynthesisScore:
    prompt = f"""
    You are evaluating the quality of an AI synthesis.

    INPUTS (what agents contributed):
    {format_inputs(raw_inputs)}

    SYNTHESIS (what the aggregator produced):
    {synthesis}

    Score 1-5 on each dimension:
    - coverage: Are key points from inputs represented?
    - accuracy: Does synthesis faithfully reflect inputs?
    - contradictions: Are disagreements noted?
    - conciseness: Is redundancy eliminated?

    Return JSON: {{"coverage": N, "accuracy": N, "contradictions": N, "conciseness": N, "reasoning": "..."}}
    """
    return await judge_llm.evaluate(prompt)
```

#### Method 2: Reference Comparison

Compare outputs against human-written references:

```python
async def eval_against_reference(output: str, reference: str) -> float:
    """Semantic similarity to known-good output."""
    output_embedding = await embed(output)
    reference_embedding = await embed(reference)
    return cosine_similarity(output_embedding, reference_embedding)
```

#### Method 3: Structural Validation

Check that outputs conform to expected structure:

```python
def validate_workspace(workspace: Workspace) -> ValidationResult:
    errors = []

    # Every hat should have synthesis
    for hat in ["white", "red", "black", "yellow", "green", "blue"]:
        if not workspace.hats[hat].synthesis:
            errors.append(f"Missing synthesis for {hat}")

    # Blue hat should have decisions
    if not workspace.artifacts.decisions:
        errors.append("No decisions produced")

    # Check provenance chains
    for decision in workspace.artifacts.decisions:
        if not decision.based_on:
            errors.append(f"Decision {decision.id} has no provenance")

    return ValidationResult(valid=len(errors) == 0, errors=errors)
```

#### Method 4: Diversity Metrics

Measure diversity of parallel agent outputs:

```python
def measure_diversity(contributions: list[str]) -> float:
    """Higher is more diverse (0-1 scale)."""
    embeddings = [embed(c) for c in contributions]

    # Average pairwise distance
    distances = []
    for i, e1 in enumerate(embeddings):
        for e2 in embeddings[i+1:]:
            distances.append(1 - cosine_similarity(e1, e2))

    return sum(distances) / len(distances) if distances else 0
```

### Evaluation Workflow

```
┌─────────────────────────────────────────────────────────┐
│                    Run Completes                        │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Structural Validation                      │
│         (schema conformance, completeness)              │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Per-Hat LLM Evaluation                     │
│     (quality scores for each hat's synthesis)           │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Diversity Measurement                      │
│      (are parallel agents producing varied output?)     │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Store Evaluation Results                   │
│       (linked to run_id for comparison)                 │
└─────────────────────────────────────────────────────────┘
```

### Comparison Harness

To compare agent configurations:

```python
async def compare_configs(
    scenario: Scenario,
    configs: list[AgentConfig],
    runs_per_config: int = 5
) -> ComparisonReport:
    """Run same scenario with different configs, compare results."""

    results = {}
    for config in configs:
        config_results = []
        for _ in range(runs_per_config):
            workspace = await run_workflow(scenario, config)
            eval_result = await evaluate_workspace(workspace)
            config_results.append(eval_result)
        results[config.name] = aggregate_results(config_results)

    return ComparisonReport(
        scenario=scenario,
        configs=configs,
        results=results,
        winner=determine_winner(results)
    )
```

### Eval Dataset

Maintain a set of benchmark scenarios:

```yaml
# evals/scenarios/product-launch.yaml
name: "Product Launch Decision"
description: "Evaluate whether to launch a new product"
scenario: |
  We are considering launching a new AI-powered health monitoring
  device for seniors. The device would track vital signs and alert
  family members to anomalies. We need to decide: should we proceed?

expected_themes:
  white:
    - market size for senior health tech
    - competitor landscape
    - regulatory requirements
  black:
    - privacy concerns
    - liability risks
    - adoption barriers for seniors
  yellow:
    - growing elderly population
    - family peace of mind
    - potential life-saving impact
  green:
    - partnership with healthcare providers
    - subscription model variations
    - integration with existing devices
```

## Consequences

### Benefits

- **Quantified quality**: Can measure improvement over time
- **Config comparison**: Can A/B test agent settings
- **Regression detection**: Know when changes hurt quality
- **Learning signal**: Eval scores guide prompt engineering

### Costs

- **Eval LLM cost**: Each run incurs additional LLM calls for judging
- **Reference creation**: Need humans to create golden references
- **Maintenance**: Eval criteria need updating as system evolves
- **Subjectivity**: "Good thinking" is inherently subjective

### Open Questions

1. How much weight to give each eval dimension?
2. How to calibrate LLM-as-judge for consistency?
3. When to involve human evaluators?
4. How to handle eval disagreements?

## References

- [ADR-000](./adr-000-architectural-principles.md): Evaluable by Design principle
- [ADR-002](./adr-002-observability-strategy.md): Traces feed into evaluation
- [LLM-as-Judge paper](https://arxiv.org/abs/2306.05685): MT-Bench and Chatbot Arena
