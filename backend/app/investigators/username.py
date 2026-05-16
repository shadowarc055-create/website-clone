from app.engine.normalization import make_entity
from app.investigators.base import Investigator
from app.models.schemas import Entity, EntityType, Finding, Relationship

SOCIAL_HOSTS = ["github.com", "x.com", "reddit.com"]


class UsernameInvestigator(Investigator):
    name = "username"
    supported_types = {EntityType.USERNAME}
    reliability = 0.58

    async def investigate(self, entity: Entity) -> list[Finding]:
        profiles = [make_entity(f"https://{host}/{entity.normalized}", EntityType.SOCIAL_PROFILE, 0.42, self.name) for host in SOCIAL_HOSTS]
        relationships = [Relationship(source=entity, target=profile, type="OWNS", confidence=0.42, provenance=self.name) for profile in profiles]
        return [Finding(investigator=self.name, title="Username enumeration candidates", summary="Generated legally accessible public profile candidates for validation.", confidence=0.42, entities=profiles, relationships=relationships)]
