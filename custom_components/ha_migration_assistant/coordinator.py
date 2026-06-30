from __future__ import annotations

from datetime import timedelta
import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_NEW_ENTITY_ID,
    CONF_OLD_ENTITY_ID,
    CONF_SCAN_BACKUPS,
    CONF_SCAN_STORAGE,
    DEFAULT_SCAN_BACKUPS,
    DEFAULT_SCAN_STORAGE,
    DOMAIN,
)
from .models import MigrationScanResult
from .scanners import get_registry_info, scan_filesystem

_LOGGER = logging.getLogger(__name__)


class MigrationAssistantCoordinator(DataUpdateCoordinator[MigrationScanResult]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(minutes=15),
        )
        self.entry = entry

    @property
    def old_entity_id(self) -> str:
        return self.entry.data[CONF_OLD_ENTITY_ID]

    @property
    def new_entity_id(self) -> str:
        return self.entry.data[CONF_NEW_ENTITY_ID]

    async def _async_update_data(self) -> MigrationScanResult:
        return await self.hass.async_add_executor_job(self._scan)

    def _scan(self) -> MigrationScanResult:
        old_entity_id = self.old_entity_id
        new_entity_id = self.new_entity_id
        scan_storage = self.entry.options.get(CONF_SCAN_STORAGE, DEFAULT_SCAN_STORAGE)
        scan_backups = self.entry.options.get(CONF_SCAN_BACKUPS, DEFAULT_SCAN_BACKUPS)
        root = Path(self.hass.config.config_dir)

        registry = get_registry_info(self.hass, old_entity_id, new_entity_id)
        matches, scanned_files = scan_filesystem(
            root=root,
            old_entity_id=old_entity_id,
            new_entity_id=new_entity_id,
            scan_storage=scan_storage,
            scan_backups=scan_backups,
        )

        result = MigrationScanResult(
            old_entity_id=old_entity_id,
            new_entity_id=new_entity_id,
            matches=matches,
            scanned_files=scanned_files,
            registry=registry,
        )
        if not registry.old_exists:
            result.warnings.append(f"Old entity {old_entity_id} was not found in the entity registry.")
        if not registry.new_exists:
            result.warnings.append(f"New entity {new_entity_id} was not found in the entity registry.")
        if registry.old_exists and registry.new_exists and registry.old_platform != registry.new_platform:
            result.warnings.append(
                f"Entity platforms differ: {registry.old_platform} → {registry.new_platform}."
            )
        return result
