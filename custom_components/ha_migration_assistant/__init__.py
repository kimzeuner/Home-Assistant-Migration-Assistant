from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
import logging
from pathlib import Path
import re

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    ATTR_ENTRY_ID,
    ATTR_FILENAME,
    DOMAIN,
    PLATFORMS,
    SERVICE_EXPORT_PLAN,
    SERVICE_RESCAN,
    SIGNAL_SCAN_UPDATED,
)
from .scanner import MigrationScanResult, scan_config

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class MigrationAssistantData:
    result: MigrationScanResult | None = None
    last_export_path: str | None = None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    data = MigrationAssistantData()
    hass.data[DOMAIN][entry.entry_id] = data
    await _async_rescan_entry(hass, entry)

    if not hass.services.has_service(DOMAIN, SERVICE_RESCAN):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RESCAN,
            _async_handle_rescan_service,
            schema=vol.Schema({vol.Optional(ATTR_ENTRY_ID): str}),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_EXPORT_PLAN):
        hass.services.async_register(
            DOMAIN,
            SERVICE_EXPORT_PLAN,
            _async_handle_export_plan_service,
            schema=vol.Schema(
                {
                    vol.Optional(ATTR_ENTRY_ID): str,
                    vol.Optional(ATTR_FILENAME): str,
                }
            ),
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if not hass.data.get(DOMAIN):
            hass.services.async_remove(DOMAIN, SERVICE_RESCAN)
            hass.services.async_remove(DOMAIN, SERVICE_EXPORT_PLAN)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def _async_rescan_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    _LOGGER.debug("Scanning migration plan for entry %s", entry.entry_id)
    result = await hass.async_add_executor_job(scan_config, hass, entry)
    hass.data[DOMAIN][entry.entry_id].result = result
    async_dispatcher_send(hass, f"{SIGNAL_SCAN_UPDATED}_{entry.entry_id}")
    _LOGGER.info(
        "Migration scan complete for %s: %s matches in %s scanned files",
        entry.title,
        result.match_count,
        result.scanned_files,
    )


async def _async_handle_rescan_service(call: ServiceCall) -> None:
    hass = call.hass
    entry_id = call.data.get(ATTR_ENTRY_ID)
    entries = _get_target_entries(hass, entry_id)
    if not entries:
        _LOGGER.warning("Rescan requested for unknown entry_id %s", entry_id)
        return

    for entry in entries:
        await _async_rescan_entry(hass, entry)


async def _async_handle_export_plan_service(call: ServiceCall) -> None:
    hass = call.hass
    entry_id = call.data.get(ATTR_ENTRY_ID)
    filename = call.data.get(ATTR_FILENAME)
    entries = _get_target_entries(hass, entry_id)
    if not entries:
        _LOGGER.warning("Export requested for unknown entry_id %s", entry_id)
        return

    for entry in entries:
        if hass.data[DOMAIN][entry.entry_id].result is None:
            await _async_rescan_entry(hass, entry)
        result = hass.data[DOMAIN][entry.entry_id].result
        if result is None:
            _LOGGER.warning("No migration scan result available for %s", entry.title)
            continue
        export_path = await hass.async_add_executor_job(
            _write_migration_plan,
            hass,
            entry,
            result,
            filename,
        )
        hass.data[DOMAIN][entry.entry_id].last_export_path = export_path
        async_dispatcher_send(hass, f"{SIGNAL_SCAN_UPDATED}_{entry.entry_id}")
        _LOGGER.info("Migration plan exported for %s to %s", entry.title, export_path)


def _get_target_entries(hass: HomeAssistant, entry_id: str | None) -> list[ConfigEntry]:
    entries = hass.config_entries.async_entries(DOMAIN)
    if entry_id is None:
        return list(entries)
    return [entry for entry in entries if entry.entry_id == entry_id]


def _safe_filename(value: str) -> str:
    value = value.lower().replace(".", "_").replace("-", "_")
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "migration_plan"


def _write_migration_plan(
    hass: HomeAssistant,
    entry: ConfigEntry,
    result: MigrationScanResult,
    filename: str | None,
) -> str:
    export_dir = Path(hass.config.path("ha_migration_assistant"))
    export_dir.mkdir(parents=True, exist_ok=True)

    if filename:
        safe_name = _safe_filename(Path(filename).stem)
    else:
        safe_name = _safe_filename(f"{result.old_entity_id}_to_{result.new_entity_id}")

    export_path = export_dir / f"{safe_name}.json"
    payload = {
        "version": "0.0.3",
        "exported_at": datetime.now(UTC).isoformat(),
        "entry_id": entry.entry_id,
        "title": entry.title,
        "read_only": True,
        "result": result.as_dict(),
    }
    export_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return export_path.as_posix()
