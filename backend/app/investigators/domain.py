import socket

from app.engine.normalization import make_entity
from app.investigators.base import Investigator
from app.models.schemas import Entity, EntityType, Finding, Relationship


class DomainInvestigator(Investigator):
    name = "domain"
    supported_types = {EntityType.DOMAIN}
    reliability = 0.76

    async def investigate(self, entity: Entity) -> list[Finding]:
        findings: list[Finding] = []
        try:
            infos = socket.getaddrinfo(entity.normalized, None, proto=socket.IPPROTO_TCP)
        except socket.gaierror:
            infos = []
        ip_entities = []
        relationships = []
        for info in infos[:5]:
            ip = info[4][0]
            ip_entity = make_entity(ip, EntityType.IP_ADDRESS, confidence=0.82, source=self.name)
            ip_entities.append(ip_entity)
            relationships.append(Relationship(source=entity, target=ip_entity, type="HOSTS", confidence=0.82, provenance=self.name))
        findings.append(
            Finding(
                investigator=self.name,
                title="DNS intelligence",
                summary=f"Resolved {len(ip_entities)} IP address pivots from DNS answers.",
                confidence=0.76 if ip_entities else 0.35,
                entities=ip_entities,
                relationships=relationships,
                raw={"resolver": "system getaddrinfo"},
            )
        )
        return findings
