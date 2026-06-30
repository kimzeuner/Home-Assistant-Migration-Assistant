from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MigrationAssistantCoordinator

SENSORS = [
    SensorEntityDescription(key="total_matches", name="Total Matches", icon="mdi:magnify-scan"),
    SensorEntityDescription(key="files_with_matches", name="Files With Matches", icon="mdi:file-search"),
    SensorEntityDescription(key="scanned_files", name="Scanned Files", icon="mdi:file-tree"),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: MigrationAssistantCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(MigrationAssistantSensor(coordinator, entry, description) for description in SENSORS)


class MigrationAssistantSensor(CoordinatorEntity[MigrationAssistantCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: MigrationAssistantCoordinator, entry: ConfigEntry, description: SensorEntityDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Migration Assistant",
            "manufacturer": "kimzeuner",
            "model": "Migration Plan",
        }

    @property
    def native_value(self):
        result = self.coordinator.data
        if result is None:
            return None
        if self.entity_description.key == "total_matches":
            return result.total_matches
        if self.entity_description.key == "files_with_matches":
            return result.files_with_matches
        if self.entity_description.key == "scanned_files":
            return result.scanned_files
        return None

    @property
    def extra_state_attributes(self):
        result = self.coordinator.data
        if result is None:
            return {}
        data = result.as_dict()
        if self.entity_description.key == "total_matches":
            data["migration_report"] = self._short_report()
            return data
        return {
            "old_entity_id": result.old_entity_id,
            "new_entity_id": result.new_entity_id,
            "category_summary": result.category_summary(),
            "file_summary": result.file_summary(),
            "warnings": result.warnings,
            "registry": result.registry.as_dict(),
        }

    def _short_report(self) -> str:
        result = self.coordinator.data
        if result is None:
            return ""
        lines = [
            f"# Migration plan: `{result.old_entity_id}` → `{result.new_entity_id}`",
            "",
            f"- Total matches: **{result.total_matches}**",
            f"- Files with matches: **{result.files_with_matches}**",
            f"- Scanned files: **{result.scanned_files}**",
        ]
        if result.warnings:
            lines.append("")
            lines.append("## Warnings")
            lines.extend(f"- {warning}" for warning in result.warnings)
        return "\n".join(lines)
