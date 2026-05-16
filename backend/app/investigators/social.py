from urllib.parse import urlparse

from app.engine.normalization import make_entity
from app.investigators.base import Investigator
from app.models.schemas import Entity, EntityType, Finding, Relationship


class SocialInvestigator(Investigator):
    name = "social"
    supported_types = {EntityType.SOCIAL_PROFILE}
    reliability = 0.62

    async def investigate(self, entity: Entity) -> list[Finding]:
        parsed = urlparse(entity.value if "://" in entity.value else f"https://{entity.value}")
        username = parsed.path.strip("/").split("/")[-1] if parsed.path.strip("/") else ""
        if not username:
            return []
        username_entity = make_entity(username, EntityType.USERNAME, confidence=0.62, source=self.name)
        return [Finding(investigator=self.name, title="Social profile parsing", summary="Extracted username pivot from public social profile URL.", confidence=0.62, entities=[username_entity], relationships=[Relationship(source=entity, target=username_entity, type="USES", confidence=0.62, provenance=self.name)])]
