from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class InvestigationRow(Base):
    __tablename__ = "investigations"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    root_entity_key: Mapped[str] = mapped_column(String(512), index=True)
    max_depth: Mapped[int]
    min_confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))


class EntityRow(Base):
    __tablename__ = "entities"
    key: Mapped[str] = mapped_column(String(512), primary_key=True)
    investigation_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("investigations.id"), index=True)
    type: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[str] = mapped_column(Text)
    normalized: Mapped[str] = mapped_column(String(512), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(128))
    entity_metadata: Mapped[dict] = mapped_column(JSON, default=dict)


class RelationshipRow(Base):
    __tablename__ = "relationships"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("investigations.id"), index=True)
    source_key: Mapped[str] = mapped_column(String(512), index=True)
    target_key: Mapped[str] = mapped_column(String(512), index=True)
    type: Mapped[str] = mapped_column(String(64), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    provenance: Mapped[str] = mapped_column(String(128))
    relationship_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
