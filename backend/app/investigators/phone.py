from app.investigators.base import Investigator
from app.models.schemas import Entity, EntityType, Finding


class PhoneInvestigator(Investigator):
    name = "phone"
    supported_types = {EntityType.PHONE}
    reliability = 0.6

    async def investigate(self, entity: Entity) -> list[Finding]:
        country_hint = "unknown"
        if entity.normalized.startswith("+1"):
            country_hint = "North America Numbering Plan"
        return [Finding(investigator=self.name, title="Phone metadata extraction", summary="Extracted non-invasive numbering metadata.", confidence=0.55, raw={"country_hint": country_hint})]
