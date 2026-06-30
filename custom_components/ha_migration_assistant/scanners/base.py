from __future__ import annotations

from pathlib import Path

from .models import MigrationMatch

MAX_CONTEXT_CHARS = 240
TEXT_EXTENSIONS = {".yaml", ".yml", ".json", ".storage", ""}
SKIP_DIRS = {".git", "deps", "tts", "www/community", "custom_components", "backups"}


def trim(value: str) -> str:
    value = value.strip()
    if len(value) <= MAX_CONTEXT_CHARS:
        return value
    return f"{value[:MAX_CONTEXT_CHARS - 3]}..."


def is_skipped(path: Path, config_dir: Path) -> bool:
    try:
        rel = path.relative_to(config_dir)
    except ValueError:
        return True
    rel_text = rel.as_posix()
    return any(rel_text == skip or rel_text.startswith(f"{skip}/") for skip in SKIP_DIRS)


def confidence_for_line(line: str, old_entity_id: str) -> tuple[int, str]:
    stripped = line.strip()
    if not stripped:
        return 50, "raw text match"
    if stripped.startswith("#"):
        return 0, "comment"
    if "entity_id" in stripped and old_entity_id in stripped:
        return 100, "entity_id field"
    if f"states('{old_entity_id}')" in stripped or f'states("{old_entity_id}")' in stripped:
        return 90, "template states() reference"
    if f"is_state('{old_entity_id}'" in stripped or f'is_state("{old_entity_id}"' in stripped:
        return 90, "template is_state() reference"
    if "{{" in stripped or "{%" in stripped:
        return 80, "template reference"
    if f'"{old_entity_id}"' in stripped or f"'{old_entity_id}'" in stripped:
        return 70, "quoted string reference"
    return 60, "raw text reference"


class BaseScanner:
    name = "base"
    category = "unknown"

    def candidate_files(self, config_dir: Path) -> list[Path]:
        raise NotImplementedError

    def scan_file(self, path: Path, config_dir: Path, old_entity_id: str, new_entity_id: str) -> list[MigrationMatch]:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return []

        rel_path = path.relative_to(config_dir).as_posix()
        matches: list[MigrationMatch] = []
        lines = text.splitlines()
        for lineno, line in enumerate(lines, start=1):
            start = 0
            while True:
                col = line.find(old_entity_id, start)
                if col == -1:
                    break
                confidence, reason = confidence_for_line(line, old_entity_id)
                if confidence > 0:
                    replacement_line = line[:col] + new_entity_id + line[col + len(old_entity_id) :]
                    matches.append(
                        MigrationMatch(
                            path=rel_path,
                            line=lineno,
                            column=col + 1,
                            current=trim(line),
                            replacement=trim(replacement_line),
                            category=self.category,
                            confidence=confidence,
                            reason=reason,
                            scanner=self.name,
                            context_before=trim(lines[lineno - 2]) if lineno > 1 else None,
                            context_after=trim(lines[lineno]) if lineno < len(lines) else None,
                        )
                    )
                start = col + len(old_entity_id)
        return matches
