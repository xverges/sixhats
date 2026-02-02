"""
Base agent abstraction for Six Thinking Hats agents.

All hat agents inherit from this base to ensure consistent:
- Contribution generation
- Provenance tracking
- Metrics collection

See ADR-005 (dapr-agents framework) and ADR-010 (workspace schema).
"""

import inspect
import time
from abc import ABC, abstractmethod
from typing import cast

from dapr_agents.llm.chat import ChatClientBase
from dapr_agents.types.message import LLMChatResponse, SystemMessage, UserMessage
from pydantic import BaseModel

from src.schemas.workspace import (
    AgentInfo,
    Contribution,
    HatType,
    Scenario,
    Workspace,
)
from src.services.workspace_service import WorkspaceService


class HatAgentConfig(BaseModel):
    """Configuration for a hat agent."""

    agent_id: str
    persona: str
    model: str = "gpt-4o-mini"  # Default to cost-effective model per ADR-007
    temperature: float = 0.7
    max_tokens: int = 2000


class HatAgentBase(ABC):
    """
    Base class for Six Thinking Hats agents.

    Each hat agent:
    - Has a specific hat type and persona
    - Analyzes scenarios from its perspective
    - Produces Contribution objects for the workspace
    """

    hat_type: HatType

    def __init__(self, config: HatAgentConfig, llm_client: ChatClientBase):
        self.config = config
        self.llm_client = llm_client

    @property
    def agent_info(self) -> AgentInfo:
        """Return agent metadata for provenance tracking."""
        return AgentInfo(
            agent_id=self.config.agent_id,
            persona=self.config.persona,
            model=self.config.model,
            temperature=self.config.temperature,
        )

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this hat's perspective."""
        ...

    @abstractmethod
    def format_scenario_prompt(self, scenario: Scenario) -> str:
        """Format the scenario into a prompt for analysis."""
        ...

    def build_system_prompt(self) -> str:
        """Build the full system prompt including persona."""
        hat_prompt = self.get_system_prompt()
        return f"You are: {self.config.persona}\n\n{hat_prompt}"

    async def analyze(self, scenario: Scenario) -> Contribution:
        """
        Analyze a scenario from this hat's perspective.

        Returns a Contribution with full provenance tracking.
        """
        # TODO(ADR-006): Wrap LLM call with trace_llm_call() for run_id correlation
        # TODO(ADR-009): Add retry logic with exponential backoff for transient failures
        start_time = time.perf_counter()

        system_prompt = self.build_system_prompt()
        user_prompt = self.format_scenario_prompt(scenario)

        result = self.llm_client.generate(
            messages=[
                SystemMessage(content=system_prompt),
                UserMessage(content=user_prompt),
            ],
        )
        # Handle both sync and async LLM clients
        # pyright doesn't narrow types based on inspect.iscoroutine()
        if inspect.iscoroutine(result):
            response = cast(LLMChatResponse, await result)  # pyright: ignore[reportGeneralTypeIssues]
        else:
            response = cast(LLMChatResponse, result)  # pyright: ignore[reportUnnecessaryCast]

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        # Extract content and token usage from response
        message = response.get_message()
        content: str = (message.content if message and message.content else "")

        # Token usage may be available on the response object
        # TODO(ADR-007): Calculate estimated cost based on model pricing
        usage = getattr(response, "usage", None)
        tokens_in = getattr(usage, "prompt_tokens", 0) if usage else 0
        tokens_out = getattr(usage, "completion_tokens", 0) if usage else 0

        return Contribution(
            agent=self.agent_info,
            hat=self.hat_type,
            content=content,
            # confidence left as None until evaluation assesses it
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=elapsed_ms,
        )

    async def run(self, workspace: Workspace) -> Workspace:
        """
        Run analysis on the workspace scenario and add contribution.

        This is the main entry point for workflow orchestration.
        """
        contribution = await self.analyze(workspace.scenario)

        svc = WorkspaceService(workspace)
        svc.add_contribution(contribution)
        svc.update_metrics(
            tokens_in=contribution.tokens_in,
            tokens_out=contribution.tokens_out,
            latency_ms=contribution.latency_ms,
            agent_calls=1,
        )
        svc.add_event(
            event_type="HAT_COMPLETED",
            actor=self.config.agent_id,
            hat=self.hat_type,
            contribution_id=contribution.contribution_id,
        )
        return workspace
