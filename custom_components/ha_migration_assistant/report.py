from __future__ import annotations

import difflib
import json
from pathlib import Path
from typing import Any

from .const import DATA_DIR
from .models import MigrationScanResult


def safe_name(value: str) -> str:
    return value.replace(".", "_").replace("/", "_").replace(" ", "_")


def build_markdown_report(result: MigrationScanResult) -> str:
    lines = [
        "# Home Assistant Migration Plan",
        "",
        f"**Old entity:** `{result.old_entity_id}`",
        f"**New entity:** `{result.new_entity_id}`",
        "",
        "## Summary",
        "",
        f"- Total matches: **{result.total_matches}**",
        f"- Files with matches: **{result.files_with_matches}**",
        f"- Scanned files: **{result.scanned_files}**",
        "",
        "## Entity Registry",
        "",
        f"- Old entity exists: **{result.registry.old_exists}**",
        f"- New entity exists: **{result.registry.new_exists}**",
        f"- Old platform: `{result.registry.old_platform}`",
        f"- New platform: `{result.registry.new_platform}`",
        "",
    ]
    if result.warnings:
        lines.extend(["## Warnings", ""])
        lines.extend([f"- {warning}" for warning in result.warnings])
        lines.append("")
    lines.extend(["## Categories", ""])
    for category, count in result.category_summary().items():
        lines.append(f"- {category}: {count}")
    lines.extend(["", "## Matches", ""])
    for match in result.matches[:200]:
        lines.extend(
            [
                f"### {match.path}:{match.line}",
                "",
                f"- Category: `{match.category}`",
                f"- Confidence: `{match.confidence}`",
                f"- Reason: {match.reason}",
                "",
                "```yaml",
            ]
        )
        if match.context_before:
            lines.append(match.context_before)
        lines.append(match.context_line)
        if match.context_after:
            lines.append(match.context_after)
        lines.extend(["```", ""])
    if len(result.matches) > 200:
        lines.append(f"_Report truncated. {len(result.matches) - 200} additional matches omitted._")
    return "\n".join(lines)


def export_plan(config_dir: str, result: MigrationScanResult) -> dict[str, Any]:
    out_dir = Path(config_dir) / DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    base = f"migration_{safe_name(result.old_entity_id)}_to_{safe_name(result.new_entity_id)}"
    json_path = out_dir / f"{base}.json"
    md_path = out_dir / f"{base}.md"
    json_path.write_text(json.dumps(result.as_dict(), indent=2), encoding="utf-8")
    md_path.write_text(build_markdown_report(result), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def generate_diff(config_dir: str, result: MigrationScanResult) -> str:
    out_dir = Path(config_dir) / DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    base = f"migration_{safe_name(result.old_entity_id)}_to_{safe_name(result.new_entity_id)}"
    diff_path = out_dir / f"{base}.diff"
    chunks: list[str] = []
    root = Path(config_dir)
    by_path: dict[str, list[int]] = {}
    for match in result.matches:
        by_path.setdefault(match.path, []).append(match.line)
    for relative_path in sorted(by_path):
        path = root / relative_path
        try:
            original = path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
        except OSError:
            continue
        modified = [line.replace(result.old_entity_id, result.new_entity_id) for line in original]
        chunks.extend(
            difflib.unified_diff(
                original,
                modified,
                fromfile=relative_path,
                tofile=relative_path,
                lineterm="",
            )
        )
    diff_path.write_text("\n".join(chunks), encoding="utf-8")
    return str(diff_path)
