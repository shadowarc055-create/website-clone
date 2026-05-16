from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.schemas import Entity, Finding


class OllamaClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def _generate(self, prompt: str) -> str | None:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    f"{self.settings.ollama_base_url}/api/generate",
                    json={"model": self.settings.ollama_model, "prompt": prompt, "stream": False},
                )
                response.raise_for_status()
                return response.json().get("response")
        except (httpx.HTTPError, json.JSONDecodeError):
            return None

    async def summarize(self, root: Entity, findings: list[Finding]) -> str:
        compact = [{"investigator": f.investigator, "title": f.title, "summary": f.summary, "confidence": f.confidence} for f in findings[-25:]]
        prompt = "Summarize this authorized OSINT investigation in concise analyst language, include confidence caveats. JSON: " + json.dumps({"root": root.model_dump(mode="json"), "findings": compact})
        generated = await self._generate(prompt)
        if generated:
            return generated.strip()
        return f"Investigation for {root.type}:{root.normalized} produced {len(findings)} findings. Local LLM unavailable; deterministic summary generated."

    async def score_relationship(self, evidence: dict[str, Any], default: float) -> float:
        if not evidence:
            return default
        return max(0.0, min(1.0, default))
