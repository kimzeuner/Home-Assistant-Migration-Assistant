from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_SCAN_UPDATED

MAX_ATTRIBUTE_MATCHES = 50

SENSOR_DESCRIPTIONS = (
    SensorEntityDescription(key="matches", name="Migration Matches", icon="mdi:file-search"),
    SensorEntityDescription(key="files", name="Migration Files", icon="mdi:file-document-alert"),
    SensorEntityDescription(key="scanned_files", name="Migration Scanned Files", icon="mdi:file-document-multiple"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        MigrationAssistantSensor(hass, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class MigrationAssistantSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
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

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{SIGNAL_SCAN_UPDATED}_{self.entry.entry_id}",
                self._handle_scan_updated,
            )
        )

    @callback
    def _handle_scan_updated(self) -> None:
        self.async_write_ha_state()

    @property
    def native_value(self):
        result = self.hass.data[DOMAIN][self.entry.entry_id].result
        if result is None:
            return None
        if self.entity_description.key == "matches":
            return result.match_count
        if self.entity_description.key == "files":
            return result.file_count
        if self.entity_description.key == "scanned_files":
            return result.scanned_files
        return None

    @property
    def extra_state_attributes(self):
        result = self.hass.data[DOMAIN][self.entry.entry_id].result
        if result is None:
            return {}
        return result.as_dict(match_limit=MAX_ATTRIBUTE_MATCHES)
