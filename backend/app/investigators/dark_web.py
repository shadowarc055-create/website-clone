from app.core.config import get_settings
from app.investigators.base import Investigator
from app.models.schemas import Entity, EntityType, Finding


class DarkWebInvestigator(Investigator):
    name = "dark_web"
    supported_types = {EntityType.EMAIL, EntityType.USERNAME, EntityType.DOMAIN, EntityType.CRYPTO_WALLET}
    reliability = 0.5

    async def investigate(self, entity: Entity) -> list[Finding]:
        if not get_settings().enable_dark_web:
            return [Finding(investigator=self.name, title="Dark web connector disabled", summary="Legally accessible dark-web indexing is disabled by policy; set ENABLE_DARK_WEB=true only for authorized deployments.", confidence=0.2, raw={"enabled": False})]
        return [Finding(investigator=self.name, title="Dark web policy gate", summary="Connector interface ready for approved indexes and audit-logged lookups.", confidence=0.45, raw={"enabled": True, "mode": "approved-index-only"})]
