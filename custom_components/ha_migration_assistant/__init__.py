from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN, SERVICE_CREATE_BACKUP, SERVICE_EXPORT_PLAN, SERVICE_GENERATE_DIFF, SERVICE_RESCAN
from .coordinator import MigrationAssistantCoordinator
from .backup import create_backup
from .report import export_plan, generate_diff

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = MigrationAssistantCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _async_register_services(hass)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok


def _async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_RESCAN):
        return

    async def async_rescan(call: ServiceCall) -> None:
        for coordinator in hass.data.get(DOMAIN, {}).values():
            await coordinator.async_request_refresh()

    async def async_export_plan(call: ServiceCall) -> None:
        for coordinator in hass.data.get(DOMAIN, {}).values():
            if coordinator.data is None:
                await coordinator.async_request_refresh()
            paths = await hass.async_add_executor_job(export_plan, hass.config.config_dir, coordinator.data)
            _LOGGER.info("Exported migration plan: %s", paths)

    async def async_generate_diff(call: ServiceCall) -> None:
        for coordinator in hass.data.get(DOMAIN, {}).values():
            if coordinator.data is None:
                await coordinator.async_request_refresh()
            path = await hass.async_add_executor_job(generate_diff, hass.config.config_dir, coordinator.data)
            _LOGGER.info("Generated migration diff: %s", path)

    async def async_create_backup(call: ServiceCall) -> None:
        for coordinator in hass.data.get(DOMAIN, {}).values():
            if coordinator.data is None:
                await coordinator.async_request_refresh()
            manifest = await hass.async_add_executor_job(create_backup, hass.config.config_dir, coordinator.data)
            _LOGGER.info("Created migration backup: %s", manifest.get("backup_dir"))

    hass.services.async_register(DOMAIN, SERVICE_RESCAN, async_rescan)
    hass.services.async_register(DOMAIN, SERVICE_EXPORT_PLAN, async_export_plan)
    hass.services.async_register(DOMAIN, SERVICE_GENERATE_DIFF, async_generate_diff)
    hass.services.async_register(DOMAIN, SERVICE_CREATE_BACKUP, async_create_backup)
