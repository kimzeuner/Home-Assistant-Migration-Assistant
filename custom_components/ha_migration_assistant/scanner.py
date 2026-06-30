from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_NEW_ENTITY_ID, CONF_OLD_ENTITY_ID, DEFAULT_SCAN_PATHS

TEXT_EXTENSIONS = {".yaml", ".yml", ".json", ".storage"}
SKIP_DIRS = {".git", "deps", "tts", "www/community", "custom_components", "backups"}
MAX_CONTEXT_CHARS = 240


@dataclass(slots=True)
class MigrationMatch:
    path: str
    line: int
    column: int
    current: str
    replacement: str
    context_before: str | None = None
    context_after: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MigrationFileSummary:
    path: str
    matches: int
    first_line: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MigrationScanResult:
    old_entity_id: str
    new_entity_id: str
    matches: list[MigrationMatch]
    scanned_files: int
    skipped_files: int

    @property
    def match_count(self) -> int:
        return len(self.matches)

    @property
    def file_count(self) -> int:
        return len({match.path for match in self.matches})

    @property
    def file_summaries(self) -> list[MigrationFileSummary]:
        counts: Counter[str] = Counter(match.path for match in self.matches)
        first_lines: dict[str, int] = {}
        for match in self.matches:
            first_lines.setdefault(match.path, match.line)
        return [
            MigrationFileSummary(path=path, matches=count, first_line=first_lines[path])
            for path, count in sorted(counts.items())
        ]

    @property
    def migration_plan_markdown(self) -> str:
        if not self.matches:
            return (
                f"No references to `{self.old_entity_id}` were found.\n\n"
                f"Proposed replacement: `{self.old_entity_id}` -> `{self.new_entity_id}`"
            )

        grouped: dict[str, list[MigrationMatch]] = defaultdict(list)
        for match in self.matches:
            grouped[match.path].append(match)

        lines = [
            "# Migration plan",
            "",
            f"Replace `{self.old_entity_id}` with `{self.new_entity_id}`.",
            "",
            f"Found **{self.match_count}** reference(s) in **{self.file_count}** file(s).",
            "",
        ]
        for path, file_matches in sorted(grouped.items()):
            lines.append(f"## `{path}`")
            for match in file_matches[:10]:
                lines.append(f"- Line {match.line}, column {match.column}: `{match.current}`")
            if len(file_matches) > 10:
                lines.append(f"- ... {len(file_matches) - 10} more match(es) in this file")
            lines.append("")
        return "\n".join(lines).strip()

    def as_dict(self, *, match_limit: int | None = None) -> dict[str, Any]:
        matches = self.matches if match_limit is None else self.matches[:match_limit]
        data = {
            "old_entity_id": self.old_entity_id,
            "new_entity_id": self.new_entity_id,
            "match_count": self.match_count,
            "file_count": self.file_count,
            "scanned_files": self.scanned_files,
            "skipped_files": self.skipped_files,
            "files": [summary.as_dict() for summary in self.file_summaries],
            "matches": [match.as_dict() for match in matches],
            "migration_plan": self.migration_plan_markdown,
        }
        if match_limit is not None and len(self.matches) > match_limit:
            data["matches_truncated"] = True
            data["matches_returned"] = len(matches)
        return data


def _trim(value: str) -> str:
    value = value.strip()
    if len(value) <= MAX_CONTEXT_CHARS:
        return value
    return f"{value[:MAX_CONTEXT_CHARS - 3]}..."


def _is_skipped(path: Path, config_dir: Path) -> bool:
    try:
        rel = path.relative_to(config_dir)
    except ValueError:
        return True
    rel_text = rel.as_posix()
    return any(rel_text == skip or rel_text.startswith(f"{skip}/") for skip in SKIP_DIRS)


def _candidate_files(config_dir: Path) -> list[Path]:
    candidates: list[Path] = []
    for item in DEFAULT_SCAN_PATHS:
        path = config_dir / item
        if path.is_file():
            candidates.append(path)
        elif path.is_dir():
            candidates.extend(
                p for p in path.rglob("*") if p.is_file() and p.suffix in TEXT_EXTENSIONS
            )
    storage_dir = config_dir / ".storage"
    if storage_dir.is_dir():
        candidates.extend(p for p in storage_dir.glob("lovelace*") if p.is_file())
    return sorted(set(candidates))


def scan_config(hass: HomeAssistant, entry: ConfigEntry) -> MigrationScanResult:
    data = {**entry.data, **entry.options}
    old_entity_id = data[CONF_OLD_ENTITY_ID]
    new_entity_id = data[CONF_NEW_ENTITY_ID]
    config_dir = Path(hass.config.path()).resolve()
    matches: list[MigrationMatch] = []
    scanned_files = 0
    skipped_files = 0

    for path in _candidate_files(config_dir):
        if _is_skipped(path, config_dir):
            skipped_files += 1
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            skipped_files += 1
            continue

        scanned_files += 1
        lines = text.splitlines()
        for lineno, line in enumerate(lines, start=1):
            start = 0
            while True:
                col = line.find(old_entity_id, start)
                if col == -1:
                    break
                replacement_line = line[:col] + new_entity_id + line[col + len(old_entity_id) :]
                matches.append(
                    MigrationMatch(
                        path=path.relative_to(config_dir).as_posix(),
                        line=lineno,
                        column=col + 1,
                        current=_trim(line),
                        replacement=_trim(replacement_line),
                        context_before=_trim(lines[lineno - 2]) if lineno > 1 else None,
                        context_after=_trim(lines[lineno]) if lineno < len(lines) else None,
                    )
                )
                start = col + len(old_entity_id)

    return MigrationScanResult(
        old_entity_id=old_entity_id,
        new_entity_id=new_entity_id,
        matches=matches,
        scanned_files=scanned_files,
        skipped_files=skipped_files,
    )
