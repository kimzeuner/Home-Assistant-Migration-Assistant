from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class MigrationMatch:
    source: str
    category: str
    path: str
    line: int
    column: int
    old_text: str
    new_text: str
    confidence: int
    reason: str
    context_before: str = ""
    context_line: str = ""
    context_after: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RegistryInfo:
    old_exists: bool = False
    new_exists: bool = False
    old_device_id: str | None = None
    new_device_id: str | None = None
    old_platform: str | None = None
    new_platform: str | None = None
    old_original_name: str | None = None
    new_original_name: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MigrationScanResult:
    old_entity_id: str
    new_entity_id: str
    matches: list[MigrationMatch] = field(default_factory=list)
    scanned_files: int = 0
    registry: RegistryInfo = field(default_factory=RegistryInfo)
    warnings: list[str] = field(default_factory=list)

    @property
    def total_matches(self) -> int:
        return len(self.matches)

    @property
    def files_with_matches(self) -> int:
        return len({match.path for match in self.matches})

    def category_summary(self) -> dict[str, int]:
        summary: dict[str, int] = {}
        for match in self.matches:
            summary[match.category] = summary.get(match.category, 0) + 1
        return dict(sorted(summary.items()))

    def file_summary(self) -> list[dict[str, Any]]:
        files: dict[str, dict[str, Any]] = {}
        for match in self.matches:
            item = files.setdefault(
                match.path,
                {"path": match.path, "category": match.category, "matches": 0, "max_confidence": 0},
            )
            item["matches"] += 1
            item["max_confidence"] = max(item["max_confidence"], match.confidence)
        return sorted(files.values(), key=lambda item: (-item["matches"], item["path"]))

    def as_dict(self) -> dict[str, Any]:
        return {
            "old_entity_id": self.old_entity_id,
            "new_entity_id": self.new_entity_id,
            "total_matches": self.total_matches,
            "files_with_matches": self.files_with_matches,
            "scanned_files": self.scanned_files,
            "category_summary": self.category_summary(),
            "file_summary": self.file_summary(),
            "registry": self.registry.as_dict(),
            "warnings": self.warnings,
            "matches": [match.as_dict() for match in self.matches],
        }
