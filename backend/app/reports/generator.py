from app.models.schemas import Finding, GraphResponse, Investigation


def generate_json_report(investigation: Investigation, findings: list[Finding], graph: GraphResponse) -> dict:
    return {
        "investigation": investigation.model_dump(mode="json"),
        "executive_summary": f"{len(findings)} findings, {len(graph.nodes)} entities, {len(graph.edges)} relationships.",
        "findings": [finding.model_dump(mode="json") for finding in findings],
        "graph": graph.model_dump(mode="json"),
        "confidence_caveats": "Automated OSINT requires analyst validation before action.",
    }
