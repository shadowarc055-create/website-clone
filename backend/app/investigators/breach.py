from app.investigators.base import Investigator
from app.models.schemas import Entity, EntityType, Finding


class BreachInvestigator(Investigator):
    name = "breach"
    supported_types = {EntityType.EMAIL, EntityType.USERNAME, EntityType.DOMAIN}
    reliability = 0.7

    async def investigate(self, entity: Entity) -> list[Finding]:
        return [Finding(investigator=self.name, title="Breach intelligence placeholder", summary="Connector boundary for licensed breach intelligence providers; no credential material is collected or exposed.", confidence=0.5, raw={"policy": "metadata-only"})]
