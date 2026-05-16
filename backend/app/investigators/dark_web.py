from app.core.config import get_settings
from app.engine.normalization import make_entity
from app.investigators.base import Investigator
from app.models.schemas import Entity, EntityType, Finding, Relationship
from app.storage.local_index import LocalJsonlIndex


class DarkWebInvestigator(Investigator):
    name = "dark_web"
    supported_types = {EntityType.EMAIL, EntityType.USERNAME, EntityType.DOMAIN, EntityType.CRYPTO_WALLET}
    reliability = 0.5

    async def investigate(self, entity: Entity) -> list[Finding]:
        settings = get_settings()
        if not settings.enable_dark_web:
            return [
                Finding(
                    investigator=self.name,
                    title="Dark web connector disabled by policy",
                    summary="Legally accessible dark-web indexing is disabled; enable only after legal review and approved index configuration.",
                    confidence=0.2,
                    raw={"enabled": False, "policy_blocked": True},
                )
            ]

        records = LocalJsonlIndex(settings.dark_web_index_path).search("entity", entity.normalized)
        findings: list[Finding] = []
        for record in records:
            related_entities = [make_entity(value, confidence=0.48, source=self.name) for value in record.get("related", [])]
            findings.append(
                Finding(
                    investigator=self.name,
                    title=f"Approved dark-web index mention: {record.get('source', 'curated index')}",
                    summary="Matched an entity in an approved, legally accessible metadata index; no authentication bypass or illicit access was performed.",
                    confidence=float(record.get("confidence", 0.45)),
                    entities=related_entities,
                    relationships=[Relationship(source=entity, target=related, type="MENTIONED_WITH", confidence=0.46, provenance=self.name) for related in related_entities],
                    raw={"source": record.get("source"), "observed": record.get("observed"), "approved_index": True},
                )
            )
        return findings or [
            Finding(
                investigator=self.name,
                title="No approved dark-web index matches",
                summary="The configured approved dark-web metadata index produced no exact normalized match.",
                confidence=0.38,
                raw={"enabled": True, "index_configured": bool(settings.dark_web_index_path)},
            )
        ]
