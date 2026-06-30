from __future__ import annotations

from pathlib import Path

from ..models import MigrationMatch


def confidence_for_line(line: str, old_entity_id: str) -> tuple[int, str]:
    stripped = line.strip()
    if stripped.startswith("#"):
        return 0, "comment"
    if f"entity_id: {old_entity_id}" in line or f"entity_id: '{old_entity_id}'" in line or f'entity_id: "{old_entity_id}"' in line:
        return 100, "direct entity_id reference"
    if f"states('{old_entity_id}')" in line or f'states("{old_entity_id}")' in line:
        return 90, "template states() reference"
    if f"is_state('{old_entity_id}'" in line or f'is_state("{old_entity_id}"' in line:
        return 90, "template is_state() reference"
    if old_entity_id in line:
        return 75, "text reference"
    return 0, "no match"


def scan_text_file(path: Path, root: Path, old_entity_id: str, new_entity_id: str, category: str, source: str) -> list[MigrationMatch]:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []

    matches: list[MigrationMatch] = []
    for index, line in enumerate(lines):
        if old_entity_id not in line:
            continue
        confidence, reason = confidence_for_line(line, old_entity_id)
        if confidence <= 0:
            continue
        matches.append(
            MigrationMatch(
                source=source,
                category=category,
                path=str(path.relative_to(root)),
                line=index + 1,
                column=line.find(old_entity_id) + 1,
                old_text=old_entity_id,
                new_text=new_entity_id,
                confidence=confidence,
                reason=reason,
                context_before=lines[index - 1] if index > 0 else "",
                context_line=line,
                context_after=lines[index + 1] if index + 1 < len(lines) else "",
            )
        )
    return matches
