from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LocalJsonlIndex:
    """Safe local JSONL lookup for licensed/synthetic intelligence indexes.

    Production deployments can mount exported, legally obtained metadata indexes without changing
    investigator code. Records are matched exactly on normalized lookup fields; no credential
    material or secrets should be stored in these files.
    """

    def __init__(self, path: str | None) -> None:
        self.path = Path(path).expanduser() if path else None

    def search(self, field: str, value: str, limit: int = 20) -> list[dict[str, Any]]:
        if self.path is None or not self.path.exists():
            return []
        matches: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                if str(record.get(field, "")).lower() == value.lower():
                    matches.append(record)
                    if len(matches) >= limit:
                        break
        return matches
