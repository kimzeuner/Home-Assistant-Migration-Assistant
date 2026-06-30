from __future__ import annotations

from pathlib import Path

from .base import scan_text_file
from ..models import MigrationMatch

TEXT_SUFFIXES = {".yaml", ".yml", ".json", ".storage", ".conf", ".txt", ".md"}
SKIP_DIRS = {".git", "deps", "tts", "www/community", "__pycache__"}
BACKUP_HINTS = {"backups", "backup", ".backup", "snapshots"}

CATEGORY_PATTERNS = [
    ("automations", "automation"),
    ("scripts", "script"),
    ("scenes", "scene"),
    ("groups", "group"),
    ("blueprints", "blueprint"),
    ("dashboards", "lovelace"),
    ("ui-lovelace", "lovelace"),
    ("templates", "template"),
    (".storage/lovelace", "storage_lovelace"),
    (".storage", "storage"),
]


def category_for_path(relative_path: str) -> str:
    normalized = relative_path.replace("\\", "/")
    for pattern, category in CATEGORY_PATTERNS:
        if pattern in normalized:
            return category
    if normalized.endswith("configuration.yaml"):
        return "config"
    return "other"


def should_skip(path: Path, root: Path, scan_storage: bool, scan_backups: bool) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    parts = set(relative.parts)
    if parts & SKIP_DIRS:
        return True
    if not scan_storage and ".storage" in parts:
        return True
    if not scan_backups and parts & BACKUP_HINTS:
        return True
    return False


def iter_candidate_files(root: Path, scan_storage: bool, scan_backups: bool):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path, root, scan_storage, scan_backups):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and ".storage" not in path.parts:
            continue
        yield path


def scan_filesystem(root: Path, old_entity_id: str, new_entity_id: str, scan_storage: bool, scan_backups: bool) -> tuple[list[MigrationMatch], int]:
    matches: list[MigrationMatch] = []
    scanned_files = 0
    for path in iter_candidate_files(root, scan_storage, scan_backups):
        scanned_files += 1
        relative = str(path.relative_to(root))
        category = category_for_path(relative)
        matches.extend(
            scan_text_file(
                path=path,
                root=root,
                old_entity_id=old_entity_id,
                new_entity_id=new_entity_id,
                category=category,
                source="filesystem",
            )
        )
    return matches, scanned_files
