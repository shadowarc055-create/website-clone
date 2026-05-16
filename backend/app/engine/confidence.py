from __future__ import annotations

from dataclasses import dataclass

from app.investigators.base import Investigator
from app.models.schemas import Entity, Finding, Relationship


@dataclass(frozen=True)
class ConfidenceScorer:
    """Deterministic confidence scoring used before optional LLM review.

    The scorer intentionally favors provenance, source reliability, and normalized evidence shape over
    opaque model output. Ollama can later summarize or explain the score, but the engine's queueing
    decisions stay deterministic and auditable.
    """

    minimum: float = 0.05
    maximum: float = 0.99

    def finding_score(self, finding: Finding, investigator: Investigator) -> float:
        score = finding.confidence * 0.65 + investigator.reliability * 0.35
        if finding.source_url:
            score += 0.04
        if finding.raw.get("validated") is True:
            score += 0.08
        if finding.raw.get("policy_blocked") is True:
            score -= 0.25
        return self._clamp(score)

    def entity_score(self, entity: Entity, finding: Finding, investigator: Investigator) -> float:
        score = entity.confidence * 0.55 + self.finding_score(finding, investigator) * 0.45
        if entity.metadata.get("validated") is True:
            score += 0.06
        return self._clamp(score)

    def relationship_score(self, relationship: Relationship, finding: Finding, investigator: Investigator) -> float:
        score = relationship.confidence * 0.6 + self.finding_score(finding, investigator) * 0.4
        if relationship.provenance == investigator.name:
            score += 0.03
        return self._clamp(score)

    def _clamp(self, score: float) -> float:
        return max(self.minimum, min(self.maximum, round(score, 4)))
