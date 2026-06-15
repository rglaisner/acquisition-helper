"""Workflow plan and agent graph models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from acquisition_helper.models.intake import TierName


class AgentNode(BaseModel):
    id: str
    role: str
    phase: str


class TaskEdge(BaseModel):
    source: str
    target: str


class WorkflowPlan(BaseModel):
    tier: TierName
    agents: list[AgentNode] = Field(default_factory=list)
    edges: list[TaskEdge] = Field(default_factory=list)
    mermaid: str = ""
    estimated_tokens_min: int = 0
    estimated_tokens_max: int = 0
    ascii_summary: str = ""
