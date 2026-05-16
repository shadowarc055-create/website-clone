from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class InvestigationRow(Base):
    __tablename__ = "investigations"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    root_entity_key: Mapped[str] = mapped_column(String(512), index=True)
    root_entity: Mapped[dict] = mapped_column(JSON)
    max_depth: Mapped[int]
    min_confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))


class EntityRow(Base):
    __tablename__ = "entities"
    investigation_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("investigations.id"), primary_key=True)
    key: Mapped[str] = mapped_column(String(512), primary_key=True)
    type: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[str] = mapped_column(Text)
    normalized: Mapped[str] = mapped_column(String(512), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(128))
    entity_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    payload: Mapped[dict] = mapped_column(JSON)


class RelationshipRow(Base):
    __tablename__ = "relationships"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("investigations.id"), index=True)
    edge_key: Mapped[str] = mapped_column(String(1600), index=True)
    source_key: Mapped[str] = mapped_column(String(512), index=True)
    target_key: Mapped[str] = mapped_column(String(512), index=True)
    type: Mapped[str] = mapped_column(String(64), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    provenance: Mapped[str] = mapped_column(String(128))
    relationship_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    payload: Mapped[dict] = mapped_column(JSON)

    __table_args__ = (UniqueConstraint("investigation_id", "edge_key", name="uq_relationship_edge"),)


class FindingRow(Base):
    __tablename__ = "findings"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("investigations.id"), index=True)
    investigator: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw: Mapped[dict] = mapped_column(JSON, default=dict)
    observed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
