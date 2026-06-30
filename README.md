# Home Assistant Migration Assistant

A read-only Home Assistant custom integration that helps you find and plan entity migrations.

Repository: <https://github.com/kimzeuner/Home-Assistant-Migration-Assistant>
Issues: <https://github.com/kimzeuner/Home-Assistant-Migration-Assistant/issues>

## What it does

The integration scans selected Home Assistant configuration areas for references to an old entity ID and prepares a migration preview for a new entity ID.

It is currently **read-only**. It does not modify YAML files, dashboards, `.storage`, or any other Home Assistant configuration.

## v0.0.4 highlights

- Modular scanner architecture
- Separate scanners for automations, scripts, scenes, groups, templates, Lovelace, `.storage` Lovelace, blueprints, and configuration
- Structured match objects
- Match categories
- Confidence scoring
- Markdown migration report in sensor attributes
- JSON export service
- Diff preview export service

## Installation

Copy this folder into Home Assistant:

```text
custom_components/ha_migration_assistant
```

Restart Home Assistant and add the integration from:

```text
Settings -> Devices & services -> Add integration -> Home Assistant Migration Assistant
```

## Services

### `ha_migration_assistant.rescan`

Rescans all configured migration entries, or a specific entry when `entry_id` is provided.

### `ha_migration_assistant.export_plan`

Exports a JSON migration plan to:

```text
/config/ha_migration_assistant/
```

### `ha_migration_assistant.generate_diff`

Exports a read-only diff preview to:

```text
/config/ha_migration_assistant/
```

This diff is only a preview. It is not applied automatically.

## Current limitations

- No file modifications yet
- No backup/restore yet
- `.storage` is scanned read-only only
- Search is entity-ID based

## Roadmap

- v0.0.5: better diff grouping and report output
- v0.0.6: backup manager
- v0.1.0: safe YAML-only migration with backup and confirmation
