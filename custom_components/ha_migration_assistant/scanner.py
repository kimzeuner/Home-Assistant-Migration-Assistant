from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_NEW_ENTITY_ID, CONF_OLD_ENTITY_ID, DEFAULT_SCAN_PATHS

TEXT_EXTENSIONS = {".yaml", ".yml", ".json", ".storage"}
SKIP_DIRS = {".git", "deps", "tts", "www/community", "custom_components"}


@dataclass
class MigrationMatch:
    path: str
    line: int
    column: int
    current: str
    replacement: str
    context: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MigrationScanResult:
    old_entity_id: str
    new_entity_id: str
    matches: list[MigrationMatch]
    scanned_files: int
    skipped_files: int

    @property
    def match_count(self) -> int:
        return len(self.matches)

    def as_dict(self) -> dict[str, Any]:
        return {
            "old_entity_id": self.old_entity_id,
            "new_entity_id": self.new_entity_id,
            "match_count": self.match_count,
            "scanned_files": self.scanned_files,
            "skipped_files": self.skipped_files,
            "matches": [match.as_dict() for match in self.matches],
        }


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
        except UnicodeDecodeError:
            skipped_files += 1
            continue
        scanned_files += 1
        for lineno, line in enumerate(text.splitlines(), start=1):
            start = 0
            while True:
                col = line.find(old_entity_id, start)
                if col == -1:
                    break
                replacement_line = line[:col] + new_entity_id + line[col + len(old_entity_id):]
                matches.append(
                    MigrationMatch(
                        path=path.relative_to(config_dir).as_posix(),
                        line=lineno,
                        column=col + 1,
                        current=line.strip(),
                        replacement=replacement_line.strip(),
                        context=line.strip(),
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
