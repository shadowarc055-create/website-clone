from app.core.config import get_settings
from app.engine.normalization import make_entity
from app.investigators.base import Investigator
from app.models.schemas import Entity, EntityType, Finding, Relationship
from app.storage.local_index import LocalJsonlIndex


class BreachInvestigator(Investigator):
    name = "breach"
    supported_types = {EntityType.EMAIL, EntityType.USERNAME, EntityType.DOMAIN}
    reliability = 0.7

    async def investigate(self, entity: Entity) -> list[Finding]:
        records = LocalJsonlIndex(get_settings().breach_index_path).search("entity", entity.normalized)
        if not records:
            return [
                Finding(
                    investigator=self.name,
                    title="No local breach metadata matches",
                    summary="Searched the configured licensed/synthetic breach metadata index and found no exact normalized match.",
                    confidence=0.46,
                    raw={"index_configured": bool(get_settings().breach_index_path)},
                )
            ]

        findings: list[Finding] = []
        for record in records:
            related_entities = [make_entity(value, confidence=0.58, source=self.name) for value in record.get("related", [])]
            relationships = [
                Relationship(source=entity, target=related, type="ASSOCIATED_WITH", confidence=0.58, provenance=self.name)
                for related in related_entities
            ]
            findings.append(
                Finding(
                    investigator=self.name,
                    title=f"Breach metadata match: {record.get('dataset', 'unknown dataset')}",
                    summary="Matched metadata from a configured legal breach-intelligence index; sensitive secret values are not stored or returned.",
                    confidence=float(record.get("confidence", 0.68)),
                    entities=related_entities,
                    relationships=relationships,
                    raw={"dataset": record.get("dataset"), "observed": record.get("observed"), "metadata_only": True, "validated": True},
                )
            )
        return findings
