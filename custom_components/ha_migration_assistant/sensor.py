from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

SENSOR_DESCRIPTIONS = (
    SensorEntityDescription(key="matches", name="Migration Matches", icon="mdi:file-search"),
    SensorEntityDescription(key="scanned_files", name="Migration Scanned Files", icon="mdi:file-document-multiple"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(MigrationAssistantSensor(hass, entry, description) for description in SENSOR_DESCRIPTIONS)


class MigrationAssistantSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, description: SensorEntityDescription) -> None:
        self.hass = hass
        self.entry = entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Community",
            "model": "Migration plan",
        }

    @property
    def native_value(self):
        result = self.hass.data[DOMAIN][self.entry.entry_id].result
        if result is None:
            return None
        if self.entity_description.key == "matches":
            return result.match_count
        if self.entity_description.key == "scanned_files":
            return result.scanned_files
        return None

    @property
    def extra_state_attributes(self):
        result = self.hass.data[DOMAIN][self.entry.entry_id].result
        if result is None:
            return {}
        data = result.as_dict()
        if len(data["matches"]) > 20:
            data["matches"] = data["matches"][:20]
            data["matches_truncated"] = True
        return data
