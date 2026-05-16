from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from uuid import UUID

from app.ai.ollama import OllamaClient
from app.engine.normalization import entity_key
from app.investigators.base import Investigator
from app.models.schemas import Entity, Finding, InvestigationStatus
from app.storage.repositories import InvestigationRepository


@dataclass(slots=True)
class QueueItem:
    entity: Entity
    depth: int
    parent_key: str | None = None


@dataclass
class EngineResult:
    visited: set[str] = field(default_factory=set)
    findings: list[Finding] = field(default_factory=list)
    stabilized: bool = False


class RecursiveInvestigationEngine:
    def __init__(self, investigators: list[Investigator], repository: InvestigationRepository, ai: OllamaClient | None = None) -> None:
        self.investigators = investigators
        self.repository = repository
        self.ai = ai or OllamaClient()

    async def run(self, investigation_id: UUID) -> EngineResult:
        investigation = await self.repository.get(investigation_id)
        if investigation is None:
            raise ValueError(f"unknown investigation: {investigation_id}")
        investigation.status = InvestigationStatus.RUNNING
        result = EngineResult()
        queue: deque[QueueItem] = deque([QueueItem(investigation.root_entity, depth=0)])
        no_new_rounds = 0

        while queue:
            item = queue.popleft()
            key = entity_key(item.entity)
            if key in result.visited or item.depth > investigation.max_depth:
                continue
            result.visited.add(key)
            await self.repository.save_entity(investigation_id, item.entity)

            findings = await self._run_supported_investigators(item.entity)
            discovered_count = 0
            for finding in findings:
                result.findings.append(finding)
                await self.repository.save_finding(investigation_id, finding)
                for relationship in finding.relationships:
                    await self.repository.save_relationship(investigation_id, relationship)
                for discovered in finding.entities:
                    await self.repository.save_entity(investigation_id, discovered)
                    discovered_key = entity_key(discovered)
                    if discovered_key not in result.visited and discovered.confidence >= investigation.min_confidence and item.depth < investigation.max_depth:
                        queue.append(QueueItem(discovered, depth=item.depth + 1, parent_key=key))
                        discovered_count += 1
            no_new_rounds = no_new_rounds + 1 if discovered_count == 0 else 0
            if no_new_rounds >= max(3, len(self.investigators)) and not queue:
                break

        result.stabilized = not queue
        investigation.status = InvestigationStatus.STABILIZED if result.stabilized else InvestigationStatus.RUNNING
        return result

    async def _run_supported_investigators(self, entity: Entity) -> list[Finding]:
        supported = [investigator for investigator in self.investigators if investigator.supports(entity)]
        batches = await asyncio.gather(*(investigator.investigate(entity) for investigator in supported), return_exceptions=True)
        findings: list[Finding] = []
        for batch in batches:
            if isinstance(batch, Exception):
                continue
            findings.extend(batch)
        return findings
