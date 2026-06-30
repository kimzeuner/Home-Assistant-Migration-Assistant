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
SERVICE_EXPORT_PLAN = "export_plan"

ATTR_ENTRY_ID = "entry_id"
ATTR_FILENAME = "filename"

SIGNAL_SCAN_UPDATED = f"{DOMAIN}_scan_updated"
