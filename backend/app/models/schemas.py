from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


class EntityType(StrEnum):
    EMAIL = "email"
    PHONE = "phone"
    USERNAME = "username"
    DOMAIN = "domain"
    IP_ADDRESS = "ip_address"
    CRYPTO_WALLET = "crypto_wallet"
    SOCIAL_PROFILE = "social_profile"
    FULL_NAME = "full_name"
    URL = "url"
    UNKNOWN = "unknown"


class InvestigationStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    STABILIZED = "stabilized"
    FAILED = "failed"


class Entity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: EntityType
    value: str
    normalized: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = "user"
    metadata: dict[str, Any] = Field(default_factory=dict)


class Relationship(BaseModel):
    source: Entity
    target: Entity
    type: str = Field(pattern=r"^[A-Z_]+$")
    confidence: float = Field(ge=0.0, le=1.0)
    provenance: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    investigator: str
    title: str
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    source_url: str | None = None
    entities: list[Entity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InvestigationCreate(BaseModel):
    type: EntityType
    value: str
    max_depth: int = Field(default=3, ge=0, le=8)
    min_confidence: float = Field(default=0.35, ge=0.0, le=1.0)
    legal_basis: str = Field(min_length=3, default="authorized OSINT investigation")


class Investigation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    root_entity: Entity
    status: InvestigationStatus = InvestigationStatus.QUEUED
    max_depth: int = 3
    min_confidence: float = 0.35
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InvestigationSummary(BaseModel):
    investigation: Investigation
    entity_count: int
    relationship_count: int
    finding_count: int
    summary: str | None = None


class GraphNode(BaseModel):
    id: str
    label: str
    type: EntityType
    confidence: float


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str
    confidence: float


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class ReportRequest(BaseModel):
    format: str = Field(default="json", pattern="^(json|pdf)$")


class UrlSubmission(BaseModel):
    url: HttpUrl
