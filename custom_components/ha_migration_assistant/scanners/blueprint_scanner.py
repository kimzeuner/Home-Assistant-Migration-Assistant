from __future__ import annotations

from pathlib import Path

from .base import BaseScanner
from .models import MatchCategory


class BlueprintScanner(BaseScanner):
    name = "blueprint_scanner"
    category = MatchCategory.BLUEPRINT.value

    def candidate_files(self, config_dir: Path) -> list[Path]:
        blueprints = config_dir / "blueprints"
        if not blueprints.is_dir():
            return []
        return [p for p in blueprints.rglob("*") if p.is_file() and p.suffix in {".yaml", ".yml"}]
