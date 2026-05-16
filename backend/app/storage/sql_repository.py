from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.engine.normalization import entity_key
from app.models.schemas import Entity, Finding, GraphEdge, GraphNode, GraphResponse, Investigation, InvestigationStatus, Relationship
from app.storage.postgres import Base, EntityRow, FindingRow, InvestigationRow, RelationshipRow
from app.storage.repositories import InvestigationRepository


def _edge_key(relationship: Relationship) -> str:
    return f"{entity_key(relationship.source)}:{relationship.type}:{entity_key(relationship.target)}"


class SqlInvestigationRepository(InvestigationRepository):
    """Async PostgreSQL-backed repository for API and worker processes.

    This repository is safe to use from separate FastAPI and Celery processes because every entity,
    finding, status transition, and deduplicated relationship is persisted in PostgreSQL.
    """

    def __init__(self, database_url: str) -> None:
        self.engine = create_async_engine(database_url, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        self._initialized = True

    async def create(self, investigation: Investigation) -> Investigation:
        await self.initialize()
        async with self.session_factory() as session, session.begin():
            row = InvestigationRow(
                id=str(investigation.id),
                status=investigation.status.value,
                root_entity_key=entity_key(investigation.root_entity),
                root_entity=investigation.root_entity.model_dump(mode="json"),
                max_depth=investigation.max_depth,
                min_confidence=investigation.min_confidence,
                created_at=investigation.created_at,
                updated_at=investigation.updated_at,
            )
            session.add(row)
        await self.save_entity(investigation.id, investigation.root_entity)
        return investigation

    async def save_entity(self, investigation_id: UUID, entity: Entity) -> None:
        await self.initialize()
        key = entity_key(entity)
        values = {
            "investigation_id": str(investigation_id),
            "key": key,
            "type": entity.type.value,
            "value": entity.value,
            "normalized": entity.normalized,
            "confidence": entity.confidence,
            "source": entity.source,
            "entity_metadata": entity.metadata,
            "payload": entity.model_dump(mode="json"),
        }
        statement = pg_insert(EntityRow).values(**values).on_conflict_do_update(
            index_elements=[EntityRow.investigation_id, EntityRow.key],
            set_={
                "confidence": values["confidence"],
                "source": values["source"],
                "entity_metadata": values["entity_metadata"],
                "payload": values["payload"],
            },
        )
        async with self.session_factory() as session, session.begin():
            await session.execute(statement)

    async def save_relationship(self, investigation_id: UUID, relationship: Relationship) -> None:
        await self.initialize()
        values = {
            "investigation_id": str(investigation_id),
            "edge_key": _edge_key(relationship),
            "source_key": entity_key(relationship.source),
            "target_key": entity_key(relationship.target),
            "type": relationship.type,
            "confidence": relationship.confidence,
            "provenance": relationship.provenance,
            "relationship_metadata": relationship.metadata,
            "payload": relationship.model_dump(mode="json"),
        }
        statement = pg_insert(RelationshipRow).values(**values).on_conflict_do_update(
            constraint="uq_relationship_edge",
            set_={
                "confidence": values["confidence"],
                "provenance": values["provenance"],
                "relationship_metadata": values["relationship_metadata"],
                "payload": values["payload"],
            },
            where=RelationshipRow.confidence <= values["confidence"],
        )
        async with self.session_factory() as session, session.begin():
            await session.execute(statement)

    async def save_finding(self, investigation_id: UUID, finding: Finding) -> None:
        await self.initialize()
        async with self.session_factory() as session, session.begin():
            session.add(
                FindingRow(
                    investigation_id=str(investigation_id),
                    investigator=finding.investigator,
                    title=finding.title,
                    summary=finding.summary,
                    confidence=finding.confidence,
                    source_url=finding.source_url,
                    raw=finding.raw,
                    observed_at=finding.observed_at,
                    payload=finding.model_dump(mode="json"),
                )
            )

    async def get(self, investigation_id: UUID) -> Investigation | None:
        await self.initialize()
        async with self.session_factory() as session:
            row = await session.get(InvestigationRow, str(investigation_id))
            if row is None:
                return None
            return Investigation(
                id=UUID(row.id),
                root_entity=Entity.model_validate(row.root_entity),
                status=InvestigationStatus(row.status),
                max_depth=row.max_depth,
                min_confidence=row.min_confidence,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    async def list_findings(self, investigation_id: UUID) -> list[Finding]:
        await self.initialize()
        async with self.session_factory() as session:
            result = await session.execute(select(FindingRow).where(FindingRow.investigation_id == str(investigation_id)).order_by(FindingRow.observed_at))
            return [Finding.model_validate(row.payload) for row in result.scalars()]

    async def update_status(self, investigation_id: UUID, status: InvestigationStatus) -> None:
        await self.initialize()
        async with self.session_factory() as session, session.begin():
            await session.execute(
                update(InvestigationRow)
                .where(InvestigationRow.id == str(investigation_id))
                .values(status=status.value, updated_at=datetime.now(timezone.utc))
            )

    async def graph(self, investigation_id: UUID) -> GraphResponse:
        await self.initialize()
        async with self.session_factory() as session:
            entity_rows = await session.execute(select(EntityRow).where(EntityRow.investigation_id == str(investigation_id)))
            relationship_rows = await session.execute(select(RelationshipRow).where(RelationshipRow.investigation_id == str(investigation_id)).order_by(RelationshipRow.id))
            nodes = [
                GraphNode(id=row.key, label=row.normalized, type=Entity.model_validate(row.payload).type, confidence=row.confidence)
                for row in entity_rows.scalars()
            ]
            edges = [
                GraphEdge(id=f"e{idx}", source=row.source_key, target=row.target_key, label=row.type, confidence=row.confidence)
                for idx, row in enumerate(relationship_rows.scalars())
            ]
            return GraphResponse(nodes=nodes, edges=edges)
