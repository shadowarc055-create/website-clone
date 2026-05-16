from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException, Response

from app.core.config import get_settings

from app.ai.ollama import OllamaClient
from app.engine.normalization import make_entity
from app.engine.recursive import RecursiveInvestigationEngine
from app.investigators import DEFAULT_INVESTIGATORS
from app.models.schemas import GraphResponse, Investigation, InvestigationCreate, InvestigationStatus, InvestigationSummary, ReportRequest
from app.reports.generator import generate_json_report, generate_pdf_report
from app.storage.repositories import repository

router = APIRouter(prefix="/api", tags=["investigations"])


@router.post("/investigations", response_model=Investigation, status_code=202)
async def create_investigation(payload: InvestigationCreate, background_tasks: BackgroundTasks) -> Investigation:
    root = make_entity(payload.value, payload.type, confidence=1.0, source="user")
    investigation = Investigation(root_entity=root, max_depth=payload.max_depth, min_confidence=payload.min_confidence)
    await repository.create(investigation)
    if get_settings().queue_mode == "celery":
        from app.queue.tasks import run_investigation

        run_investigation.delay(str(investigation.id))
    else:
        background_tasks.add_task(_run_investigation, investigation.id)
    return investigation


@router.get("/investigations/{investigation_id}", response_model=InvestigationSummary)
async def get_investigation(investigation_id: UUID) -> InvestigationSummary:
    investigation = await repository.get(investigation_id)
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    graph = await repository.graph(investigation_id)
    findings = await repository.list_findings(investigation_id)
    summary = await OllamaClient().summarize(investigation.root_entity, findings) if investigation.status == InvestigationStatus.STABILIZED else None
    return InvestigationSummary(investigation=investigation, entity_count=len(graph.nodes), relationship_count=len(graph.edges), finding_count=len(findings), summary=summary)


@router.get("/investigations/{investigation_id}/graph", response_model=GraphResponse)
async def get_graph(investigation_id: UUID) -> GraphResponse:
    if await repository.get(investigation_id) is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return await repository.graph(investigation_id)


@router.get("/investigations/{investigation_id}/timeline")
async def get_timeline(investigation_id: UUID) -> list[dict]:
    if await repository.get(investigation_id) is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    findings = await repository.list_findings(investigation_id)
    return [finding.model_dump(mode="json") for finding in sorted(findings, key=lambda f: f.observed_at)]


@router.post("/investigations/{investigation_id}/reports")
async def create_report(investigation_id: UUID, request: ReportRequest) -> dict | Response:
    investigation = await repository.get(investigation_id)
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    findings = await repository.list_findings(investigation_id)
    graph = await repository.graph(investigation_id)
    if request.format == "pdf":
        return Response(
            content=generate_pdf_report(investigation, findings, graph),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=investigation-{investigation_id}.pdf"},
        )
    return generate_json_report(investigation, findings, graph)


async def _run_investigation(investigation_id: UUID) -> None:
    engine = RecursiveInvestigationEngine(DEFAULT_INVESTIGATORS, repository)
    await engine.run(investigation_id)
