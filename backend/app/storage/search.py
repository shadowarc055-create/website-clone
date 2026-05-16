from app.models.schemas import Finding


def finding_document(finding: Finding) -> dict:
    return {
        "investigator": finding.investigator,
        "title": finding.title,
        "summary": finding.summary,
        "confidence": finding.confidence,
        "source_url": finding.source_url,
        "observed_at": finding.observed_at.isoformat(),
        "entities": [entity.model_dump(mode="json") for entity in finding.entities],
    }
