from __future__ import annotations

from io import BytesIO

from app.models.schemas import Finding, GraphResponse, Investigation


def generate_json_report(investigation: Investigation, findings: list[Finding], graph: GraphResponse) -> dict:
    return {
        "investigation": investigation.model_dump(mode="json"),
        "executive_summary": f"{len(findings)} findings, {len(graph.nodes)} entities, {len(graph.edges)} relationships.",
        "findings": [finding.model_dump(mode="json") for finding in findings],
        "graph": graph.model_dump(mode="json"),
        "confidence_caveats": "Automated OSINT requires analyst validation before action.",
    }


def generate_pdf_report(investigation: Investigation, findings: list[Finding], graph: GraphResponse) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 48

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(48, y, "Autonomous OSINT Investigation Report")
    y -= 28
    pdf.setFont("Helvetica", 10)
    pdf.drawString(48, y, f"Investigation: {investigation.id}")
    y -= 16
    pdf.drawString(48, y, f"Root: {investigation.root_entity.type}:{investigation.root_entity.normalized}")
    y -= 16
    pdf.drawString(48, y, f"Status: {investigation.status} | Entities: {len(graph.nodes)} | Relationships: {len(graph.edges)} | Findings: {len(findings)}")
    y -= 28

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(48, y, "Findings")
    y -= 18
    pdf.setFont("Helvetica", 9)
    for finding in findings[:50]:
        if y < 72:
            pdf.showPage()
            y = height - 48
            pdf.setFont("Helvetica", 9)
        pdf.drawString(48, y, f"[{finding.confidence:.2f}] {finding.investigator}: {finding.title}"[:110])
        y -= 13
        pdf.drawString(64, y, finding.summary[:115])
        y -= 17

    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(48, 36, "Automated OSINT output requires analyst validation before action.")
    pdf.save()
    return buffer.getvalue()
