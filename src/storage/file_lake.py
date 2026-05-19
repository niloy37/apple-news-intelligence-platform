"""Local file-backed lakehouse helpers used by scripts and tests."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from src.config import Settings, get_settings


@dataclass
class LocalLakehouse:
    """Write raw, bronze, silver, and gold artifacts as JSONL/JSON locally."""

    settings: Settings = field(default_factory=get_settings)

    def layer_dir(self, layer: str) -> Path:
        path = self.settings.exports_dir / layer
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_jsonl(self, layer: str, name: str, records: Iterable[dict[str, Any]]) -> Path:
        path = self.layer_dir(layer) / name
        with path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, default=str) + "\n")
        return path

    def write_json(self, layer: str, name: str, payload: Any) -> Path:
        path = self.layer_dir(layer) / name
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return path

    def read_json(self, layer: str, name: str, default: Any) -> Any:
        path = self.layer_dir(layer) / name
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def timestamped_name(self, prefix: str, suffix: str = "jsonl") -> str:
        return f"{prefix}_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.{suffix}"
