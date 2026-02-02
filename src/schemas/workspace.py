"""
Workspace schema for Six Thinking Hats multi-agent system.

See ADR-010 for design rationale.
"""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    """Status of a thinking run."""

    INITIALIZED = "initialized"
    RUNNING = "running"
    WAITING_FOR_HUMAN = "waiting_for_human"
    COMPLETED = "completed"
    FAILED = "failed"


class RunMode(str, Enum):
    """Mode of operation for the workflow."""

    AUTO = "auto"  # Fully automated
    HUMAN_BLUE = "human_blue"  # Human acts as Blue Hat
    HYBRID = "hybrid"  # Human can intervene at any point


class HatType(str, Enum):
    """The six thinking hats."""

    WHITE = "white"  # Facts, data, information
    RED = "red"  # Emotions, intuition, gut feelings
    BLACK = "black"  # Caution, risks, problems
    YELLOW = "yellow"  # Benefits, optimism, value
    GREEN = "green"  # Creativity, alternatives, new ideas
    BLUE = "blue"  # Process control, synthesis, decisions


# --- Run Metadata ---


class RunMetadata(BaseModel):
    """Metadata about a thinking run."""

    run_id: str = Field(default_factory=lambda: str(uuid4()))
    status: RunStatus = RunStatus.INITIALIZED
    mode: RunMode = RunMode.AUTO
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    protocol: str = "six_thinking_hats:v1"
    initiator: str = "system"
    tags: list[str] = Field(default_factory=list)


# --- Scenario ---


class ScenarioInputs(BaseModel):
    """Supporting inputs for a scenario."""

    documents: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
    notes: str = ""


class Scenario(BaseModel):
    """The problem or decision to evaluate."""

    title: str
    problem_statement: str
    context: str = ""
    objectives: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    inputs: ScenarioInputs = Field(default_factory=ScenarioInputs)


# --- Agent Contribution (Raw) ---


class AgentInfo(BaseModel):
    """Information about the agent that produced a contribution."""

    agent_id: str
    persona: str
    model: str
    temperature: float


class Contribution(BaseModel):
    """A raw contribution from an agent. Immutable once created."""

    contribution_id: str = Field(default_factory=lambda: str(uuid4()))
    agent: AgentInfo
    hat: HatType
    content: str
    structured: dict | None = None  # Hat-specific structured data
    confidence: float | None = None  # None = not assessed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: list[str] = Field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0


# --- Synthesis ---


class Synthesis(BaseModel):
    """Aggregated synthesis of multiple contributions."""

    synthesis_id: str = Field(default_factory=lambda: str(uuid4()))
    hat: HatType
    summary: str
    key_points: list[str] = Field(default_factory=list)
    clusters: list[dict] = Field(default_factory=list)  # Grouped themes
    contradictions: list[str] = Field(default_factory=list)
    confidence: float | None = None  # None = not assessed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    derived_from: list[str] = Field(default_factory=list)  # contribution_ids


# --- Hat State ---


class HatState(BaseModel):
    """State for a single thinking hat."""

    raw: list[Contribution] = Field(default_factory=list)
    synthesis: Synthesis | None = None


# --- Artifacts ---


class Decision(BaseModel):
    """A decision made during or after the thinking process."""

    decision_id: str = Field(default_factory=lambda: str(uuid4()))
    statement: str
    rationale: str
    based_on: list[str] = Field(default_factory=list)  # synthesis_ids or contribution_ids
    made_by: str  # "human" or "auto-blue"
    confidence: float | None = None  # None = not assessed
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ActionItem(BaseModel):
    """An action item derived from the thinking process."""

    action_id: str = Field(default_factory=lambda: str(uuid4()))
    task: str
    owner: str = "unassigned"
    priority: str = "medium"
    due_by: datetime | None = None
    origin_hat: HatType
    based_on: list[str] = Field(default_factory=list)  # contribution_ids or synthesis_ids
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OpenQuestion(BaseModel):
    """A question that remains unanswered."""

    question_id: str = Field(default_factory=lambda: str(uuid4()))
    question: str
    origin_hat: HatType
    priority: str = "medium"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Artifacts(BaseModel):
    """Cross-hat outputs and decisions."""

    global_summary: str | None = None
    decisions: list[Decision] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    open_questions: list[OpenQuestion] = Field(default_factory=list)


# --- Audit ---


class AuditEvent(BaseModel):
    """An event in the audit log."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str  # HAT_STARTED, HAT_COMPLETED, HUMAN_INPUT, ERROR, etc.
    hat: HatType | None = None
    actor: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: dict = Field(default_factory=dict)


class AuditMetrics(BaseModel):
    """Aggregate metrics for a run."""

    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_latency_ms: int = 0
    estimated_cost_usd: float = 0.0
    agent_call_count: int = 0
    aggregation_call_count: int = 0


class Audit(BaseModel):
    """Audit trail and metrics for a run."""

    events: list[AuditEvent] = Field(default_factory=list)
    metrics: AuditMetrics = Field(default_factory=AuditMetrics)


# --- Full Workspace ---


def _default_hats() -> dict[HatType, HatState]:
    """Create default empty hat states."""
    return {hat: HatState() for hat in HatType}


class Workspace(BaseModel):
    """
    The complete workspace for a Six Thinking Hats run.

    This is the central data structure that flows through the workflow.
    See ADR-010 for design rationale.
    """

    run: RunMetadata = Field(default_factory=RunMetadata)
    scenario: Scenario
    hats: dict[HatType, HatState] = Field(default_factory=_default_hats)
    artifacts: Artifacts = Field(default_factory=Artifacts)
    audit: Audit = Field(default_factory=Audit)

    model_config = {"use_enum_values": True}
