from __future__ import annotations

from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..const import CONF_NEW_ENTITY_ID, CONF_OLD_ENTITY_ID
from .base import BaseScanner, is_skipped
from .blueprint_scanner import BlueprintScanner
from .lovelace_scanners import LovelaceScanner, StorageLovelaceScanner
from .models import MigrationMatch, MigrationScanResult
from .yaml_scanners import (
    AutomationScanner,
    ConfigurationScanner,
    GroupScanner,
    SceneScanner,
    ScriptScanner,
    TemplateScanner,
)

SCANNERS: tuple[BaseScanner, ...] = (
    AutomationScanner(),
    ScriptScanner(),
    SceneScanner(),
    GroupScanner(),
    ConfigurationScanner(),
    TemplateScanner(),
    LovelaceScanner(),
    StorageLovelaceScanner(),
    BlueprintScanner(),
)


def scan_config(hass: HomeAssistant, entry: ConfigEntry) -> MigrationScanResult:
    data = {**entry.data, **entry.options}
    old_entity_id = data[CONF_OLD_ENTITY_ID]
    new_entity_id = data[CONF_NEW_ENTITY_ID]
    config_dir = Path(hass.config.path()).resolve()

    matches: list[MigrationMatch] = []
    scanned_files = 0
    skipped_files = 0
    seen: set[Path] = set()
    scanner_names: list[str] = []

    for scanner in SCANNERS:
        scanner_names.append(scanner.name)
        for path in scanner.candidate_files(config_dir):
            try:
                resolved = path.resolve()
            except OSError:
                skipped_files += 1
                continue
            if resolved in seen:
                continue
            seen.add(resolved)
            if is_skipped(resolved, config_dir):
                skipped_files += 1
                continue
            file_matches = scanner.scan_file(resolved, config_dir, old_entity_id, new_entity_id)
            scanned_files += 1
            matches.extend(file_matches)

    matches.sort(key=lambda item: (item.path, item.line, item.column))
    return MigrationScanResult(
        old_entity_id=old_entity_id,
        new_entity_id=new_entity_id,
        matches=matches,
        scanned_files=scanned_files,
        skipped_files=skipped_files,
        scanners=scanner_names,
    )


__all__ = ["MigrationScanResult", "MigrationMatch", "scan_config"]
