#!/usr/bin/env python
"""
End-to-end demo of the Black Hat agent with a real LLM call via Dapr.

This example demonstrates:
1. Creating a scenario for analysis
2. Running the Black Hat agent to identify risks
3. Viewing the workspace with contribution and audit trail

Prerequisites:
    1. Install Dapr CLI: https://docs.dapr.io/getting-started/install-dapr-cli/
    2. Initialize Dapr: dapr init
    3. Set your API key: export OPENAI_API_KEY="your-api-key"

Usage:
    dapr run --app-id black-hat-demo --resources-path ./components -- uv run python examples/black_hat_demo.py
"""

import asyncio
import sys
from pathlib import Path

from dapr_agents.llm import DaprChatClient
from dapr_agents.observability import DaprAgentsInstrumentor
from phoenix.otel import register

from src.agents.black_hat import create_black_hat_agent
from src.schemas.workspace import HatType, Scenario, Workspace


def create_sample_scenario() -> Scenario:
    """Create a realistic scenario for Black Hat analysis."""
    return Scenario(
        title="Zero Trust Security Implementation",
        problem_statement=(
            "Implement zero trust architecture across all systems after "
            "a security audit revealed critical vulnerabilities."
        ),
        context=(
            "Recent penetration test found 12 critical vulnerabilities. "
            "Currently using VPN-based perimeter security. 150 internal applications. "
            "Mix of cloud and on-premise systems. Board demanding action after industry breach."
        ),
        objectives=[
            "Eliminate all critical vulnerabilities within 90 days",
            "Implement identity-based access for all applications",
            "Deploy continuous monitoring and anomaly detection",
            "Achieve SOC 2 Type II certification",
        ],
        constraints=[
            "Budget: $500K for tools and implementation",
            "Cannot disrupt business operations during rollout",
            "Must support legacy applications that cannot be modified",
            "Security team is only 4 people",
        ],
        assumptions=[
            "All applications can integrate with SSO",
            "Users will adopt MFA without significant resistance",
            "Cloud providers' security tools are sufficient",
            "Vendors will support required integrations",
        ],
        success_criteria=[
            "Zero critical vulnerabilities in follow-up audit",
            "100% of applications behind identity-aware proxy",
            "Mean time to detect threats under 15 minutes",
            "Pass SOC 2 Type II audit",
        ],
    )


def print_workspace_summary(workspace: Workspace) -> None:
    """Print a formatted summary of the workspace after analysis."""
    print("\n" + "=" * 80)
    print("WORKSPACE SUMMARY")
    print("=" * 80)

    # Run metadata
    print(f"\nRun ID: {workspace.run.run_id}")
    print(f"Status: {workspace.run.status}")
    print(f"Created: {workspace.run.created_at}")

    # Scenario
    print(f"\nScenario: {workspace.scenario.title}")

    # Black Hat contribution
    black_hat_state = workspace.hats[HatType.BLACK]
    if black_hat_state.raw:
        contribution = black_hat_state.raw[0]
        print("\n" + "-" * 80)
        print("BLACK HAT ANALYSIS")
        print("-" * 80)
        print(f"\nAgent: {contribution.agent.agent_id}")
        print(f"Model: {contribution.agent.model}")
        print(f"Tokens: {contribution.tokens_in} in, {contribution.tokens_out} out")
        print(f"Latency: {contribution.latency_ms}ms")
        print(f"\n{contribution.content}")

    # Metrics
    metrics = workspace.audit.metrics
    print("\n" + "-" * 80)
    print("METRICS")
    print("-" * 80)
    print(f"Total tokens: {metrics.total_tokens_in + metrics.total_tokens_out}")
    print(f"Agent calls: {metrics.agent_call_count}")
    print(f"Total latency: {metrics.total_latency_ms}ms")

    # Audit events
    print("\n" + "-" * 80)
    print("AUDIT TRAIL")
    print("-" * 80)
    for event in workspace.audit.events:
        print(f"  [{event.timestamp}] {event.event_type} by {event.actor}")


async def main() -> int:
    """Run the Black Hat agent demo."""
    print("Six Thinking Hats - Black Hat Agent Demo")
    print("=" * 80)

    # Create the LLM client via Dapr sidecar
    print("\n1. Initializing Dapr LLM client...")
    llm_client = DaprChatClient()

    # Create the Black Hat agent
    print("2. Creating Black Hat agent...")
    agent = create_black_hat_agent(
        llm_client=llm_client,
        agent_id="black-hat-demo",
        model="gpt-4o-mini",
        temperature=0.7,
    )

    # Create the scenario
    print("3. Creating scenario for analysis...")
    scenario = create_sample_scenario()
    print(f"   Scenario: {scenario.title}")

    # Create workspace and run analysis
    print("4. Running Black Hat analysis...")
    workspace = Workspace(scenario=scenario)
    workspace = await agent.run(workspace)

    # Display results
    print_workspace_summary(workspace)

    print("\n" + "=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    tracer_provider = register(
        project_name=Path(__file__).parent.stem,
        protocol="http/protobuf",
    )
    instrumentor = DaprAgentsInstrumentor()
    instrumentor.instrument(tracer_provider=tracer_provider)

    sys.exit(asyncio.run(main()))
