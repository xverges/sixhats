"""
Service for managing Workspace operations.

Handles mutations, audit logging, and metrics tracking for workspaces.
Persistence integration will be added here.
"""

from datetime import datetime

from src.schemas.workspace import (
    AuditEvent,
    Contribution,
    HatType,
    Synthesis,
    Workspace,
)


class WorkspaceService:
    """Service for managing Workspace operations."""

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    @property
    def workspace(self) -> Workspace:
        """Return the managed workspace."""
        return self._workspace

    def add_contribution(self, contribution: Contribution) -> None:
        """Add a contribution to the appropriate hat."""
        self._workspace.hats[contribution.hat].raw.append(contribution)
        self._workspace.run.updated_at = datetime.utcnow()

    def set_synthesis(self, hat: HatType, synthesis: Synthesis) -> None:
        """Set the synthesis for a hat."""
        self._workspace.hats[hat].synthesis = synthesis
        self._workspace.run.updated_at = datetime.utcnow()

    def add_event(
        self,
        event_type: str,
        actor: str,
        hat: HatType | None = None,
        **data,
    ) -> None:
        """Add an audit event."""
        self._workspace.audit.events.append(
            AuditEvent(
                event_type=event_type,
                hat=hat,
                actor=actor,
                data=data,
            )
        )

    def update_metrics(
        self,
        tokens_in: int = 0,
        tokens_out: int = 0,
        latency_ms: int = 0,
        cost_usd: float = 0.0,
        agent_calls: int = 0,
        aggregation_calls: int = 0,
    ) -> None:
        """Update aggregate metrics."""
        m = self._workspace.audit.metrics
        m.total_tokens_in += tokens_in
        m.total_tokens_out += tokens_out
        m.total_latency_ms += latency_ms
        m.estimated_cost_usd += cost_usd
        m.agent_call_count += agent_calls
        m.aggregation_call_count += aggregation_calls
