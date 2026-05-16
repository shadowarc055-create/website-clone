from __future__ import annotations

import hashlib
import ipaddress
import re
from urllib.parse import urlparse

from app.models.schemas import Entity, EntityType

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[0-9][0-9 .()\-]{6,}$")
CRYPTO_RE = re.compile(r"^(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{25,90})$")


def normalize_value(entity_type: EntityType, value: str) -> str:
    value = value.strip()
    if entity_type in {EntityType.EMAIL, EntityType.DOMAIN, EntityType.USERNAME, EntityType.SOCIAL_PROFILE, EntityType.URL}:
        value = value.lower()
    if entity_type == EntityType.DOMAIN:
        value = value.removeprefix("www.").rstrip(".")
    if entity_type == EntityType.SOCIAL_PROFILE:
        parsed = urlparse(value)
        if parsed.netloc:
            return f"{parsed.netloc.lower()}{parsed.path.rstrip('/').lower()}"
    if entity_type == EntityType.PHONE:
        return re.sub(r"[^0-9+]", "", value)
    return value


def infer_type(value: str) -> EntityType:
    candidate = value.strip()
    if EMAIL_RE.match(candidate):
        return EntityType.EMAIL
    try:
        ipaddress.ip_address(candidate)
        return EntityType.IP_ADDRESS
    except ValueError:
        pass
    if CRYPTO_RE.match(candidate):
        return EntityType.CRYPTO_WALLET
    parsed = urlparse(candidate)
    if parsed.scheme and parsed.netloc:
        host = parsed.netloc.lower()
        if any(s in host for s in ("github.com", "x.com", "twitter.com", "linkedin.com", "facebook.com", "instagram.com")):
            return EntityType.SOCIAL_PROFILE
        return EntityType.URL
    if PHONE_RE.match(candidate):
        return EntityType.PHONE
    if "." in candidate and " " not in candidate:
        return EntityType.DOMAIN
    if " " in candidate:
        return EntityType.FULL_NAME
    return EntityType.USERNAME


def make_entity(value: str, entity_type: EntityType | None = None, confidence: float = 1.0, source: str = "system") -> Entity:
    resolved_type = entity_type or infer_type(value)
    normalized = normalize_value(resolved_type, value)
    fingerprint = hashlib.sha256(f"{resolved_type}:{normalized}".encode()).hexdigest()
    return Entity(type=resolved_type, value=value.strip(), normalized=normalized, confidence=confidence, source=source, metadata={"fingerprint": fingerprint})


def entity_key(entity: Entity) -> str:
    return f"{entity.type}:{entity.normalized}"
