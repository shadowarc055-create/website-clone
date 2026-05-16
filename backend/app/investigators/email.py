from app.engine.normalization import make_entity
from app.investigators.base import Investigator
from app.models.schemas import Entity, EntityType, Finding, Relationship


class EmailInvestigator(Investigator):
    name = "email"
    supported_types = {EntityType.EMAIL}
    reliability = 0.72

    async def investigate(self, entity: Entity) -> list[Finding]:
        local, domain = entity.normalized.split("@", 1)
        username = make_entity(local, EntityType.USERNAME, confidence=0.74, source=self.name)
        domain_entity = make_entity(domain, EntityType.DOMAIN, confidence=0.86, source=self.name)
        return [
            Finding(
                investigator=self.name,
                title="Email decomposition",
                summary="Derived username and domain pivots from email syntax.",
                confidence=0.78,
                entities=[username, domain_entity],
                relationships=[
                    Relationship(source=entity, target=username, type="USES", confidence=0.72, provenance=self.name),
                    Relationship(source=entity, target=domain_entity, type="ASSOCIATED_WITH", confidence=0.86, provenance=self.name),
                ],
            )
        ]
