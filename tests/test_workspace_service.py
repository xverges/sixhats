"""Tests for the workspace service."""

import pytest

from src.schemas.workspace import (
    AgentInfo,
    Contribution,
    HatType,
    Scenario,
    Synthesis,
    Workspace,
)
from src.services.workspace_service import WorkspaceService


class TestContribution:
    """Tests for Contribution model."""

    def test_contribution_has_unique_id(self):
        """Test that each contribution gets a unique ID."""
        agent = AgentInfo(
            agent_id="test",
            persona="Test",
            model="test",
            temperature=0.5,
        )
        c1 = Contribution(agent=agent, hat=HatType.BLACK, content="Risk 1")
        c2 = Contribution(agent=agent, hat=HatType.BLACK, content="Risk 2")
        assert c1.contribution_id != c2.contribution_id


class TestWorkspace:
    """Tests for Workspace model."""

    @pytest.fixture
    def sample_scenario(self) -> Scenario:
        """Create a sample scenario for testing."""
        return Scenario(
            title="Test Decision",
            problem_statement="Should we proceed with option A?",
            context="We have limited resources",
        )

    @pytest.fixture
    def sample_workspace(self, sample_scenario: Scenario) -> Workspace:
        """Create a sample workspace for testing."""
        return Workspace(scenario=sample_scenario)

    def test_workspace_creation(self, sample_workspace: Workspace):
        """Test workspace initializes with all six hats."""
        assert len(sample_workspace.hats) == 6
        for hat_type in HatType:
            assert hat_type in sample_workspace.hats
            assert sample_workspace.hats[hat_type].raw == []
            assert sample_workspace.hats[hat_type].synthesis is None

    def test_add_contribution(self, sample_workspace: Workspace):
        """Test adding a contribution to a workspace via service."""
        agent = AgentInfo(
            agent_id="black-hat-001",
            persona="Critical Analyst",
            model="gpt-4o-mini",
            temperature=0.7,
        )
        contribution = Contribution(
            agent=agent,
            hat=HatType.BLACK,
            content="Risk identified: timeline too aggressive",
        )

        svc = WorkspaceService(sample_workspace)
        svc.add_contribution(contribution)

        assert len(sample_workspace.hats[HatType.BLACK].raw) == 1
        assert sample_workspace.hats[HatType.BLACK].raw[0].content == contribution.content

    def test_set_synthesis(self, sample_workspace: Workspace):
        """Test setting synthesis for a hat via service."""
        synthesis = Synthesis(
            hat=HatType.BLACK,
            summary="Three major risks identified",
            key_points=["Timeline risk", "Budget risk", "Technical risk"],
            derived_from=["contrib-1", "contrib-2"],
        )

        svc = WorkspaceService(sample_workspace)
        svc.set_synthesis(HatType.BLACK, synthesis)

        assert sample_workspace.hats[HatType.BLACK].synthesis is not None
        assert (
            sample_workspace.hats[HatType.BLACK].synthesis.summary == "Three major risks identified"
        )

    def test_update_metrics(self, sample_workspace: Workspace):
        """Test updating aggregate metrics via service."""
        svc = WorkspaceService(sample_workspace)
        svc.update_metrics(
            tokens_in=100,
            tokens_out=50,
            latency_ms=1500,
            cost_usd=0.01,
            agent_calls=1,
        )

        metrics = sample_workspace.audit.metrics
        assert metrics.total_tokens_in == 100
        assert metrics.total_tokens_out == 50
        assert metrics.total_latency_ms == 1500
        assert metrics.estimated_cost_usd == 0.01
        assert metrics.agent_call_count == 1

    def test_add_event(self, sample_workspace: Workspace):
        """Test adding audit events via service."""
        svc = WorkspaceService(sample_workspace)
        svc.add_event(
            event_type="HAT_STARTED",
            actor="orchestrator",
            hat=HatType.BLACK,
            message="Starting black hat analysis",
        )

        assert len(sample_workspace.audit.events) == 1
        event = sample_workspace.audit.events[0]
        assert event.event_type == "HAT_STARTED"
        assert event.hat == HatType.BLACK
        assert event.data["message"] == "Starting black hat analysis"

    def test_workspace_serialization_roundtrip(self, sample_workspace: Workspace):
        """Test workspace can be serialized and deserialized without data loss."""
        json_str = sample_workspace.model_dump_json()
        restored = Workspace.model_validate_json(json_str)

        assert restored.scenario.title == sample_workspace.scenario.title
        assert restored.run.run_id == sample_workspace.run.run_id
        assert len(restored.hats) == len(sample_workspace.hats)
