from __future__ import annotations

DOMAIN = "ha_migration_assistant"
PLATFORMS = ["sensor"]

CONF_OLD_ENTITY_ID = "old_entity_id"
CONF_NEW_ENTITY_ID = "new_entity_id"

DEFAULT_SCAN_PATHS = [
    "automations.yaml",
    "scripts.yaml",
    "scenes.yaml",
    "groups.yaml",
    "configuration.yaml",
    "ui-lovelace.yaml",
    "dashboards",
]

SERVICE_RESCAN = "rescan"
ATTR_ENTRY_ID = "entry_id"
SIGNAL_SCAN_UPDATED = f"{DOMAIN}_scan_updated"
