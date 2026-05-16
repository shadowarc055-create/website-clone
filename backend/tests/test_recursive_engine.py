from uuid import uuid4

import pytest

from app.engine.normalization import entity_key, make_entity
from app.engine.recursive import RecursiveInvestigationEngine
from app.investigators.email import EmailInvestigator
from app.investigators.username import UsernameInvestigator
from app.models.schemas import EntityType, Investigation
from app.storage.repositories import InMemoryInvestigationRepository


@pytest.mark.asyncio
async def test_recursive_engine_pivots_and_stabilizes() -> None:
    repository = InMemoryInvestigationRepository()
    root = make_entity("analyst@example.com", EntityType.EMAIL, source="test")
    investigation = Investigation(id=uuid4(), root_entity=root, max_depth=2, min_confidence=0.35)
    await repository.create(investigation)

    result = await RecursiveInvestigationEngine([EmailInvestigator(), UsernameInvestigator()], repository).run(investigation.id)
    graph = await repository.graph(investigation.id)

    assert result.stabilized is True
    assert entity_key(root) in result.visited
    assert any(node.type == EntityType.USERNAME and node.label == "analyst" for node in graph.nodes)
    assert any(edge.label == "USES" for edge in graph.edges)


@pytest.mark.asyncio
async def test_depth_limit_prevents_unbounded_pivoting() -> None:
    repository = InMemoryInvestigationRepository()
    root = make_entity("analyst", EntityType.USERNAME, source="test")
    investigation = Investigation(id=uuid4(), root_entity=root, max_depth=0, min_confidence=0.35)
    await repository.create(investigation)

    result = await RecursiveInvestigationEngine([UsernameInvestigator()], repository).run(investigation.id)

    assert result.visited == {entity_key(root)}
    assert len(result.findings) == 1
