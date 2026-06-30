from __future__ import annotations

from dataclasses import dataclass
import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import ATTR_ENTRY_ID, DOMAIN, PLATFORMS, SERVICE_RESCAN, SIGNAL_SCAN_UPDATED
from .scanner import MigrationScanResult, scan_config

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class MigrationAssistantData:
    result: MigrationScanResult | None = None


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

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if not hass.data.get(DOMAIN):
            hass.services.async_remove(DOMAIN, SERVICE_RESCAN)
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
    entries = hass.config_entries.async_entries(DOMAIN)
    if entry_id is not None:
        entries = [entry for entry in entries if entry.entry_id == entry_id]
        if not entries:
            _LOGGER.warning("Rescan requested for unknown entry_id %s", entry_id)
            return

    for entry in entries:
        await _async_rescan_entry(hass, entry)
