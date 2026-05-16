from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from app.engine.normalization import entity_key
from app.models.schemas import Entity, Finding, GraphEdge, GraphNode, GraphResponse, Investigation, Relationship


class InvestigationRepository:
    async def create(self, investigation: Investigation) -> Investigation:
        raise NotImplementedError

    async def save_entity(self, investigation_id: UUID, entity: Entity) -> None:
        raise NotImplementedError

    async def save_relationship(self, investigation_id: UUID, relationship: Relationship) -> None:
        raise NotImplementedError

    async def save_finding(self, investigation_id: UUID, finding: Finding) -> None:
        raise NotImplementedError

    async def get(self, investigation_id: UUID) -> Investigation | None:
        raise NotImplementedError

    async def list_findings(self, investigation_id: UUID) -> list[Finding]:
        raise NotImplementedError

    async def graph(self, investigation_id: UUID) -> GraphResponse:
        raise NotImplementedError


class InMemoryInvestigationRepository(InvestigationRepository):
    def __init__(self) -> None:
        self.investigations: dict[UUID, Investigation] = {}
        self.entities: dict[UUID, dict[str, Entity]] = defaultdict(dict)
        self.relationships: dict[UUID, list[Relationship]] = defaultdict(list)
        self.findings: dict[UUID, list[Finding]] = defaultdict(list)

    async def create(self, investigation: Investigation) -> Investigation:
        self.investigations[investigation.id] = investigation
        await self.save_entity(investigation.id, investigation.root_entity)
        return investigation

    async def save_entity(self, investigation_id: UUID, entity: Entity) -> None:
        self.entities[investigation_id][entity_key(entity)] = entity

    async def save_relationship(self, investigation_id: UUID, relationship: Relationship) -> None:
        self.relationships[investigation_id].append(relationship)

    async def save_finding(self, investigation_id: UUID, finding: Finding) -> None:
        self.findings[investigation_id].append(finding)

    async def get(self, investigation_id: UUID) -> Investigation | None:
        return self.investigations.get(investigation_id)

    async def list_findings(self, investigation_id: UUID) -> list[Finding]:
        return self.findings[investigation_id]

    async def graph(self, investigation_id: UUID) -> GraphResponse:
        nodes = [GraphNode(id=entity_key(entity), label=entity.normalized, type=entity.type, confidence=entity.confidence) for entity in self.entities[investigation_id].values()]
        edges = [GraphEdge(id=f"e{idx}", source=entity_key(rel.source), target=entity_key(rel.target), label=rel.type, confidence=rel.confidence) for idx, rel in enumerate(self.relationships[investigation_id])]
        return GraphResponse(nodes=nodes, edges=edges)


repository = InMemoryInvestigationRepository()
