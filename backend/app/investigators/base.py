from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.schemas import Entity, EntityType, Finding


class Investigator(ABC):
    name: str
    supported_types: set[EntityType]
    reliability: float = 0.65

    def supports(self, entity: Entity) -> bool:
        return entity.type in self.supported_types

    @abstractmethod
    async def investigate(self, entity: Entity) -> list[Finding]:
        """Return findings for an entity without mutating global state."""
