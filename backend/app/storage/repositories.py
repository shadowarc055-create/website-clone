from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from app.engine.normalization import entity_key
from app.models.schemas import Entity, Finding, GraphEdge, GraphNode, GraphResponse, Investigation, InvestigationStatus, Relationship


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

    async def update_status(self, investigation_id: UUID, status: InvestigationStatus) -> None:
        raise NotImplementedError

    async def graph(self, investigation_id: UUID) -> GraphResponse:
        raise NotImplementedError


class InMemoryInvestigationRepository(InvestigationRepository):
    def __init__(self) -> None:
        self.investigations: dict[UUID, Investigation] = {}
        self.entities: dict[UUID, dict[str, Entity]] = defaultdict(dict)
        self.relationships: dict[UUID, dict[str, Relationship]] = defaultdict(dict)
        self.findings: dict[UUID, list[Finding]] = defaultdict(list)

    async def create(self, investigation: Investigation) -> Investigation:
        self.investigations[investigation.id] = investigation
        await self.save_entity(investigation.id, investigation.root_entity)
        return investigation

    async def save_entity(self, investigation_id: UUID, entity: Entity) -> None:
        self.entities[investigation_id][entity_key(entity)] = entity

    async def save_relationship(self, investigation_id: UUID, relationship: Relationship) -> None:
        key = f"{entity_key(relationship.source)}:{relationship.type}:{entity_key(relationship.target)}"
        existing = self.relationships[investigation_id].get(key)
        if existing is None or relationship.confidence >= existing.confidence:
            self.relationships[investigation_id][key] = relationship

    async def save_finding(self, investigation_id: UUID, finding: Finding) -> None:
        self.findings[investigation_id].append(finding)

    async def get(self, investigation_id: UUID) -> Investigation | None:
        return self.investigations.get(investigation_id)

    async def list_findings(self, investigation_id: UUID) -> list[Finding]:
        return self.findings[investigation_id]

    async def update_status(self, investigation_id: UUID, status: InvestigationStatus) -> None:
        if investigation_id in self.investigations:
            self.investigations[investigation_id].status = status

    async def graph(self, investigation_id: UUID) -> GraphResponse:
        nodes = [GraphNode(id=entity_key(entity), label=entity.normalized, type=entity.type, confidence=entity.confidence) for entity in self.entities[investigation_id].values()]
        edges = [GraphEdge(id=f"e{idx}", source=entity_key(rel.source), target=entity_key(rel.target), label=rel.type, confidence=rel.confidence) for idx, rel in enumerate(self.relationships[investigation_id].values())]
        return GraphResponse(nodes=nodes, edges=edges)


repository = InMemoryInvestigationRepository()
