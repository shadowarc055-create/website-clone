from app.engine.normalization import entity_key
from app.models.schemas import Relationship


MERGE_ENTITY = """
MERGE (e:Entity {key: $key})
SET e.type = $type, e.value = $value, e.normalized = $normalized, e.confidence = $confidence
"""


def relationship_cypher(relationship: Relationship) -> tuple[str, dict]:
    rel_type = relationship.type.upper()
    query = f"""
    MERGE (s:Entity {{key: $source_key}})
    MERGE (t:Entity {{key: $target_key}})
    MERGE (s)-[r:{rel_type}]->(t)
    SET r.confidence = $confidence, r.provenance = $provenance, r.metadata = $metadata
    """
    return query, {
        "source_key": entity_key(relationship.source),
        "target_key": entity_key(relationship.target),
        "confidence": relationship.confidence,
        "provenance": relationship.provenance,
        "metadata": relationship.metadata,
    }
