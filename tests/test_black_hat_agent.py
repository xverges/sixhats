"""Tests for the Black Hat agent."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agents.black_hat import (
    BlackHatAgent,
    create_black_hat_agent,
)
from src.schemas.workspace import (
    HatType,
    Scenario,
    Workspace,
)


class MockMessage:
    """Mock message returned by LLM."""

    def __init__(self, content: str):
        self.content = content


class MockResponse:
    """Mock LLM response."""

    def __init__(self, content: str, prompt_tokens: int = 100, completion_tokens: int = 50):
        self._content = content
        self.usage = MagicMock()
        self.usage.prompt_tokens = prompt_tokens
        self.usage.completion_tokens = completion_tokens

    def get_message(self) -> MockMessage:
        return MockMessage(self._content)


class MockChatClient:
    """Mock ChatClientBase for testing."""

    def __init__(self, response_content: str = "Mock risk analysis"):
        self.response_content = response_content
        self.generate = AsyncMock(return_value=MockResponse(response_content))


@pytest.fixture
def sample_scenario() -> Scenario:
    """Create a sample scenario for testing."""
    return Scenario(
        title="Cloud Migration",
        problem_statement="Should we migrate our monolith to microservices on Kubernetes?",
        context="Currently running a Django monolith on EC2",
        objectives=["Improve scalability", "Reduce deployment time"],
        constraints=["Budget: $100k", "Timeline: 6 months"],
        assumptions=["Team can learn Kubernetes", "AWS costs will decrease"],
        success_criteria=["99.9% uptime", "Deploy in < 10 minutes"],
    )


@pytest.fixture
def mock_llm_client() -> MockChatClient:
    """Create a mock LLM client."""
    return MockChatClient(
        response_content="""# Critical Risks

## 1. Timeline Risk (High)
- **Description**: 6 months is aggressive for a full microservices migration
- **Trigger**: Team inexperience with Kubernetes
- **Impact**: Project delays, budget overrun
- **Confidence**: High

## 2. Complexity Risk (High)
- **Description**: Microservices introduce distributed system complexity
- **Trigger**: Network failures, service discovery issues
- **Impact**: Increased debugging time, potential outages
- **Confidence**: High

## Challenged Assumptions
- "Team can learn Kubernetes" - Learning curve is steep
- "AWS costs will decrease" - Often costs increase initially
"""
    )


@pytest.fixture
def black_hat_agent(mock_llm_client: MockChatClient) -> BlackHatAgent:
    """Create a Black Hat agent with mock client."""
    return create_black_hat_agent(
        llm_client=mock_llm_client,
        agent_id="test-black-hat",
        model="gpt-4o-mini",
        temperature=0.7,
    )


class TestBlackHatAgent:
    """Tests for BlackHatAgent."""

    def test_format_scenario_prompt_minimal(self, black_hat_agent: BlackHatAgent):
        """Test formatting a minimal scenario shows expected structure."""
        scenario = Scenario(
            title="Simple Test",
            problem_statement="Should we do X?",
        )
        prompt = black_hat_agent.format_scenario_prompt(scenario)

        assert "# Scenario: Simple Test" in prompt
        assert "Should we do X?" in prompt
        assert "Black Hat perspective" in prompt

    @pytest.mark.asyncio
    async def test_analyze(
        self,
        black_hat_agent: BlackHatAgent,
        mock_llm_client: MockChatClient,
        sample_scenario: Scenario,
    ):
        """Test analyzing a scenario produces a valid contribution."""
        contribution = await black_hat_agent.analyze(sample_scenario)

        mock_llm_client.generate.assert_called_once()

        assert contribution.hat == HatType.BLACK
        assert contribution.agent.agent_id == "test-black-hat"
        assert "Timeline Risk" in contribution.content
        assert contribution.tokens_in == 100
        assert contribution.tokens_out == 50
        assert contribution.latency_ms >= 0

    @pytest.mark.asyncio
    async def test_run_updates_workspace(
        self,
        black_hat_agent: BlackHatAgent,
        sample_scenario: Scenario,
    ):
        """Test running agent updates workspace with contribution and metrics."""
        workspace = Workspace(scenario=sample_scenario)

        assert len(workspace.hats[HatType.BLACK].raw) == 0
        assert workspace.audit.metrics.agent_call_count == 0

        updated_workspace = await black_hat_agent.run(workspace)

        # Contribution was added
        assert len(updated_workspace.hats[HatType.BLACK].raw) == 1
        contribution = updated_workspace.hats[HatType.BLACK].raw[0]
        assert contribution.hat == HatType.BLACK

        # Metrics were updated
        assert updated_workspace.audit.metrics.agent_call_count == 1
        assert updated_workspace.audit.metrics.total_tokens_in == 100
        assert updated_workspace.audit.metrics.total_tokens_out == 50

        # Audit event was recorded
        events = [e for e in updated_workspace.audit.events if e.event_type == "HAT_COMPLETED"]
        assert len(events) == 1
        assert events[0].hat == HatType.BLACK
        assert events[0].actor == "test-black-hat"
