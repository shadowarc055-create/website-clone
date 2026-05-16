from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from uuid import UUID

from app.ai.ollama import OllamaClient
from app.engine.confidence import ConfidenceScorer
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
    def __init__(self, investigators: list[Investigator], repository: InvestigationRepository, ai: OllamaClient | None = None, scorer: ConfidenceScorer | None = None) -> None:
        self.investigators = investigators
        self.repository = repository
        self.ai = ai or OllamaClient()
        self.scorer = scorer or ConfidenceScorer()

    async def run(self, investigation_id: UUID) -> EngineResult:
        investigation = await self.repository.get(investigation_id)
        if investigation is None:
            raise ValueError(f"unknown investigation: {investigation_id}")
        investigation.status = InvestigationStatus.RUNNING
        await self.repository.update_status(investigation_id, InvestigationStatus.RUNNING)
        result = EngineResult()
        queue: deque[QueueItem] = deque([QueueItem(investigation.root_entity, depth=0)])
        queued_keys = {entity_key(investigation.root_entity)}
        no_new_rounds = 0

        while queue:
            item = queue.popleft()
            key = entity_key(item.entity)
            queued_keys.discard(key)
            if key in result.visited or item.depth > investigation.max_depth:
                continue
            result.visited.add(key)
            await self.repository.save_entity(investigation_id, item.entity)

            investigator_findings = await self._run_supported_investigators(item.entity)
            discovered_count = 0
            for investigator, finding in investigator_findings:
                finding.confidence = self.scorer.finding_score(finding, investigator)
                result.findings.append(finding)
                await self.repository.save_finding(investigation_id, finding)
                for relationship in finding.relationships:
                    relationship.confidence = self.scorer.relationship_score(relationship, finding, investigator)
                    await self.repository.save_relationship(investigation_id, relationship)
                for discovered in finding.entities:
                    discovered.confidence = self.scorer.entity_score(discovered, finding, investigator)
                    await self.repository.save_entity(investigation_id, discovered)
                    discovered_key = entity_key(discovered)
                    if discovered_key not in result.visited and discovered_key not in queued_keys and discovered.confidence >= investigation.min_confidence and item.depth < investigation.max_depth:
                        queue.append(QueueItem(discovered, depth=item.depth + 1, parent_key=key))
                        queued_keys.add(discovered_key)
                        discovered_count += 1
            no_new_rounds = no_new_rounds + 1 if discovered_count == 0 else 0
            if no_new_rounds >= max(3, len(self.investigators)) and not queue:
                break

        result.stabilized = not queue
        investigation.status = InvestigationStatus.STABILIZED if result.stabilized else InvestigationStatus.RUNNING
        await self.repository.update_status(investigation_id, investigation.status)
        return result

    async def _run_supported_investigators(self, entity: Entity) -> list[tuple[Investigator, Finding]]:
        supported = [investigator for investigator in self.investigators if investigator.supports(entity)]
        batches = await asyncio.gather(*(investigator.investigate(entity) for investigator in supported), return_exceptions=True)
        findings: list[tuple[Investigator, Finding]] = []
        for investigator, batch in zip(supported, batches, strict=True):
            if isinstance(batch, Exception):
                findings.append((investigator, Finding(investigator=investigator.name, title="Investigator failed", summary=str(batch), confidence=0.05, raw={"error": type(batch).__name__})))
                continue
            findings.extend((investigator, finding) for finding in batch)
        return findings
