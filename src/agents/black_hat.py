"""
Black Hat Agent - Critical thinking and risk analysis.

The Black Hat represents:
- Caution and critical judgment
- Risk identification and assessment
- Problem spotting and devil's advocacy
- Logical negativity (not emotional pessimism)

See ADR-008 for evaluation criteria:
- Risk coverage: Are all significant risks identified?
- Severity calibration: Are risk levels appropriately assessed?
"""

from dapr_agents.llm.chat import ChatClientBase

from src.agents.base import HatAgentBase, HatAgentConfig
from src.schemas.workspace import HatType, Scenario

BLACK_HAT_SYSTEM_PROMPT = """\
You are a critical thinking expert wearing the Black Hat from Edward de Bono's
Six Thinking Hats methodology.

Your role is to identify risks, problems, and potential failures. You apply
logical negativity—not pessimism or emotional rejection, but careful critical
analysis.

## Your Responsibilities:
1. **Identify Risks**: What could go wrong? What are the dangers?
2. **Spot Weaknesses**: Where are the flaws in this plan or idea?
3. **Challenge Assumptions**: Which assumptions might be wrong?
4. **Consider Obstacles**: What barriers exist? What might block success?
5. **Assess Severity**: How serious is each risk? What's the impact if it occurs?

## Guidelines:
- Be thorough but fair—identify real risks, not imagined ones
- Prioritize risks by likelihood and impact
- Be specific: "The database might fail" is weak; "The database lacks redundancy
  and a single node failure would cause 4+ hours of downtime" is strong
- Consider technical, operational, financial, and human risks
- Don't suggest solutions (that's for other hats)—focus on identifying problems

## Output Format:
Structure your analysis as:
1. **Critical Risks** (high likelihood OR high impact)
2. **Moderate Risks** (medium likelihood AND medium impact)
3. **Minor Concerns** (low likelihood AND low impact)
4. **Challenged Assumptions** (assumptions that may not hold)

For each risk, provide:
- Clear description of the risk
- Potential trigger or cause
- Likely impact if it occurs
- Confidence level (high/medium/low) in this assessment"""


class BlackHatAgent(HatAgentBase):
    """
    Black Hat agent for critical analysis and risk identification.

    Analyzes scenarios to identify:
    - Risks and potential failures
    - Weaknesses in plans or proposals
    - Challenged assumptions
    - Obstacles and barriers
    """

    hat_type = HatType.BLACK

    def __init__(self, config: HatAgentConfig, llm_client: ChatClientBase):
        super().__init__(config, llm_client)

    def get_system_prompt(self) -> str:
        """Return the Black Hat system prompt."""
        return BLACK_HAT_SYSTEM_PROMPT

    def format_scenario_prompt(self, scenario: Scenario) -> str:
        """Format the scenario for Black Hat analysis."""
        parts = [
            f"# Scenario: {scenario.title}",
            "",
            "## Problem Statement",
            scenario.problem_statement,
        ]

        if scenario.context:
            parts.extend(["", "## Context", scenario.context])

        if scenario.objectives:
            parts.extend(["", "## Objectives"])
            for obj in scenario.objectives:
                parts.append(f"- {obj}")

        if scenario.constraints:
            parts.extend(["", "## Constraints"])
            for constraint in scenario.constraints:
                parts.append(f"- {constraint}")

        if scenario.assumptions:
            parts.extend(["", "## Stated Assumptions"])
            for assumption in scenario.assumptions:
                parts.append(f"- {assumption}")

        if scenario.success_criteria:
            parts.extend(["", "## Success Criteria"])
            for criterion in scenario.success_criteria:
                parts.append(f"- {criterion}")

        parts.extend(
            [
                "",
                "---",
                "",
                "Please analyze this scenario from the Black Hat perspective. "
                "Identify all significant risks, weaknesses, and challenged assumptions.",
            ]
        )

        return "\n".join(parts)


def create_black_hat_agent(
    llm_client: ChatClientBase,
    agent_id: str = "black-hat-001",
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
) -> BlackHatAgent:
    """
    Factory function to create a configured Black Hat agent.

    Args:
        llm_client: The LLM client for making API calls
        agent_id: Unique identifier for this agent instance
        model: Model to use (default: gpt-4o-mini per ADR-007)
        temperature: Sampling temperature (default: 0.7)

    Returns:
        Configured BlackHatAgent instance
    """
    config = HatAgentConfig(
        agent_id=agent_id,
        persona="Critical Analyst - Black Hat Thinker",
        model=model,
        temperature=temperature,
    )
    return BlackHatAgent(config, llm_client)
