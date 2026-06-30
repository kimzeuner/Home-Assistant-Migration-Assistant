# Changelog

## v0.0.5

### Changed

- Changed `integration_type` from `helper` to `service` to avoid Home Assistant treating the integration as a Helper integration.
- Updated export payload version to `0.0.5`.
- Updated config-flow descriptions to remove outdated v0.0.1 wording.

### Added

- Added `icons.json` for service icons.
- Added local brand assets under `custom_components/ha_migration_assistant/brand/`.

### Kept from v0.0.4

- Modular scanner engine.
- Match categories.
- Confidence scores.
- Markdown migration report attributes.
- JSON export service.
- Diff export service.
- Read-only behavior.

## v0.0.4

### Added

- Modular scanner architecture.
- Match categories for automations, scripts, scenes, groups, templates, Lovelace, `.storage`, blueprints, and general config files.
- Confidence score per match.
- Better Markdown migration report.
- Service `ha_migration_assistant.generate_diff`.
- `.diff` export into `/config/ha_migration_assistant/`.

### Changed

- Scanner result model now uses structured match objects.
- Sensor attributes now include richer match metadata.

## v0.0.3

### Added

- Service `ha_migration_assistant.export_plan`.
- JSON export into `/config/ha_migration_assistant/`.
- `last_export_path` sensor attribute.

## v0.0.2

### Added

- Service `ha_migration_assistant.rescan`.
- Improved match attributes.
- File summary attributes.
- Markdown migration plan attribute.

## v0.0.1

### Added

- Initial read-only scanner.
- Config flow.
- Options flow.
- Summary sensors.
