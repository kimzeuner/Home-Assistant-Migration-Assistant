from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from ..models import RegistryInfo


def get_registry_info(hass: HomeAssistant, old_entity_id: str, new_entity_id: str) -> RegistryInfo:
    registry = er.async_get(hass)
    old_entry = registry.async_get(old_entity_id)
    new_entry = registry.async_get(new_entity_id)
    return RegistryInfo(
        old_exists=old_entry is not None,
        new_exists=new_entry is not None,
        old_device_id=old_entry.device_id if old_entry else None,
        new_device_id=new_entry.device_id if new_entry else None,
        old_platform=old_entry.platform if old_entry else None,
        new_platform=new_entry.platform if new_entry else None,
        old_original_name=old_entry.original_name if old_entry else None,
        new_original_name=new_entry.original_name if new_entry else None,
    )
