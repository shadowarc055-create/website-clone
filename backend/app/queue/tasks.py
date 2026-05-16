import asyncio
from uuid import UUID

from app.engine.recursive import RecursiveInvestigationEngine
from app.investigators import DEFAULT_INVESTIGATORS
from app.queue.celery_app import celery_app
from app.storage.repositories import repository


@celery_app.task(name="app.queue.tasks.run_investigation")
def run_investigation(investigation_id: str) -> dict:
    result = asyncio.run(RecursiveInvestigationEngine(DEFAULT_INVESTIGATORS, repository).run(UUID(investigation_id)))
    return {"visited": len(result.visited), "findings": len(result.findings), "stabilized": result.stabilized}
