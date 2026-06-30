from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .const import DATA_DIR
from .models import MigrationScanResult
from .report import safe_name


def create_backup(config_dir: str, result: MigrationScanResult) -> dict[str, Any]:
    """Create a file-level backup for all files referenced by the current scan result.

    The function is intentionally conservative: it only copies files that contain
    matches in the latest scan result and never modifies the originals.
    """
    root = Path(config_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"migration_{safe_name(result.old_entity_id)}_to_{safe_name(result.new_entity_id)}_{timestamp}"
    backup_dir = root / DATA_DIR / "backups" / base_name
    files_dir = backup_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    backed_up_files: list[dict[str, Any]] = []
    skipped_files: list[dict[str, str]] = []

    for relative_path in sorted({match.path for match in result.matches}):
        source = root / relative_path
        if not source.exists() or not source.is_file():
            skipped_files.append({"path": relative_path, "reason": "missing_or_not_file"})
            continue
        try:
            # Prevent path traversal in case a future scanner returns unexpected paths.
            source.resolve().relative_to(root.resolve())
        except ValueError:
            skipped_files.append({"path": relative_path, "reason": "outside_config_dir"})
            continue

        destination = files_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        backed_up_files.append(
            {
                "path": relative_path,
                "backup_path": str(destination),
                "size": destination.stat().st_size,
            }
        )

    manifest = {
        "created_at": timestamp,
        "old_entity_id": result.old_entity_id,
        "new_entity_id": result.new_entity_id,
        "total_matches": result.total_matches,
        "files_with_matches": result.files_with_matches,
        "backup_dir": str(backup_dir),
        "backed_up_files": backed_up_files,
        "skipped_files": skipped_files,
    }
    manifest_path = backup_dir / "backup_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    return manifest
