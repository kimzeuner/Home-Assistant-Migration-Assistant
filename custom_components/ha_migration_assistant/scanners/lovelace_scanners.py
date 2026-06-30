from __future__ import annotations

from pathlib import Path

from .base import BaseScanner
from .models import MatchCategory


class LovelaceScanner(BaseScanner):
    name = "lovelace_scanner"
    category = MatchCategory.DASHBOARD.value

    def candidate_files(self, config_dir: Path) -> list[Path]:
        candidates: list[Path] = []
        for name in ("ui-lovelace.yaml", "lovelace.yaml"):
            path = config_dir / name
            if path.is_file():
                candidates.append(path)
        dashboards = config_dir / "dashboards"
        if dashboards.is_dir():
            candidates.extend(
                p for p in dashboards.rglob("*") if p.is_file() and p.suffix in {".yaml", ".yml", ".json"}
            )
        return candidates


class StorageLovelaceScanner(BaseScanner):
    name = "storage_lovelace_scanner"
    category = MatchCategory.STORAGE.value

    def candidate_files(self, config_dir: Path) -> list[Path]:
        storage_dir = config_dir / ".storage"
        if not storage_dir.is_dir():
            return []
        return [p for p in storage_dir.glob("lovelace*") if p.is_file()]
