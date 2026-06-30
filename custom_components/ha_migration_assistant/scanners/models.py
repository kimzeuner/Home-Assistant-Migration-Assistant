from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class MatchCategory(StrEnum):
    AUTOMATION = "automation"
    SCRIPT = "script"
    SCENE = "scene"
    GROUP = "group"
    DASHBOARD = "dashboard"
    BLUEPRINT = "blueprint"
    TEMPLATE = "template"
    STORAGE = "storage"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class MigrationMatch:
    path: str
    line: int
    column: int
    current: str
    replacement: str
    category: str
    confidence: int
    reason: str
    scanner: str
    context_before: str | None = None
    context_after: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MigrationFileSummary:
    path: str
    category: str
    matches: int
    first_line: int
    max_confidence: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MigrationCategorySummary:
    category: str
    matches: int
    files: int
    max_confidence: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MigrationScanResult:
    old_entity_id: str
    new_entity_id: str
    matches: list[MigrationMatch]
    scanned_files: int
    skipped_files: int
    scanners: list[str]

    @property
    def match_count(self) -> int:
        return len(self.matches)

    @property
    def file_count(self) -> int:
        return len({match.path for match in self.matches})

    @property
    def file_summaries(self) -> list[MigrationFileSummary]:
        grouped: dict[str, list[MigrationMatch]] = defaultdict(list)
        for match in self.matches:
            grouped[match.path].append(match)

        summaries: list[MigrationFileSummary] = []
        for path, matches in sorted(grouped.items()):
            categories = Counter(match.category for match in matches)
            category = categories.most_common(1)[0][0] if categories else MatchCategory.UNKNOWN.value
            summaries.append(
                MigrationFileSummary(
                    path=path,
                    category=category,
                    matches=len(matches),
                    first_line=min(match.line for match in matches),
                    max_confidence=max(match.confidence for match in matches),
                )
            )
        return summaries

    @property
    def category_summaries(self) -> list[MigrationCategorySummary]:
        grouped: dict[str, list[MigrationMatch]] = defaultdict(list)
        for match in self.matches:
            grouped[match.category].append(match)
        return [
            MigrationCategorySummary(
                category=category,
                matches=len(matches),
                files=len({match.path for match in matches}),
                max_confidence=max(match.confidence for match in matches),
            )
            for category, matches in sorted(grouped.items())
        ]

    @property
    def migration_plan_markdown(self) -> str:
        if not self.matches:
            return (
                "# Migration report\n\n"
                f"No references to `{self.old_entity_id}` were found.\n\n"
                f"Proposed replacement: `{self.old_entity_id}` -> `{self.new_entity_id}`"
            )

        grouped: dict[str, list[MigrationMatch]] = defaultdict(list)
        for match in self.matches:
            grouped[match.category].append(match)

        lines = [
            "# Migration report",
            "",
            f"Replace `{self.old_entity_id}` with `{self.new_entity_id}`.",
            "",
            f"Found **{self.match_count}** reference(s) in **{self.file_count}** file(s).",
            "",
            "## Summary by category",
            "",
            "| Category | Matches | Files | Max confidence |",
            "| --- | ---: | ---: | ---: |",
        ]
        for summary in self.category_summaries:
            lines.append(
                f"| {summary.category} | {summary.matches} | {summary.files} | {summary.max_confidence}% |"
            )

        lines.extend(["", "## Matches", ""])
        for category, matches in sorted(grouped.items()):
            lines.append(f"### {category}")
            by_file: dict[str, list[MigrationMatch]] = defaultdict(list)
            for match in matches:
                by_file[match.path].append(match)
            for path, file_matches in sorted(by_file.items()):
                lines.append(f"- `{path}`: {len(file_matches)} match(es)")
                for match in file_matches[:10]:
                    lines.append(
                        f"  - line {match.line}, confidence {match.confidence}%: `{match.current}`"
                    )
                if len(file_matches) > 10:
                    lines.append(f"  - ... {len(file_matches) - 10} more match(es)")
            lines.append("")
        return "\n".join(lines).strip()

    def as_dict(self, *, match_limit: int | None = None) -> dict[str, Any]:
        matches = self.matches if match_limit is None else self.matches[:match_limit]
        data: dict[str, Any] = {
            "old_entity_id": self.old_entity_id,
            "new_entity_id": self.new_entity_id,
            "match_count": self.match_count,
            "file_count": self.file_count,
            "scanned_files": self.scanned_files,
            "skipped_files": self.skipped_files,
            "scanners": self.scanners,
            "categories": [summary.as_dict() for summary in self.category_summaries],
            "files": [summary.as_dict() for summary in self.file_summaries],
            "matches": [match.as_dict() for match in matches],
            "migration_plan": self.migration_plan_markdown,
        }
        if match_limit is not None and len(self.matches) > match_limit:
            data["matches_truncated"] = True
            data["matches_returned"] = len(matches)
        return data
