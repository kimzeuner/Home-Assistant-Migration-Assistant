# Changelog

## v0.0.4

### Added

- Modular scanner architecture.
- Scanner categories for automations, scripts, scenes, groups, templates, Lovelace, `.storage` Lovelace, blueprints, and configuration.
- Structured migration match objects.
- Match confidence scoring.
- Category summaries in scan attributes.
- Improved Markdown migration report.
- Service `ha_migration_assistant.generate_diff` for read-only diff preview export.
- Attribute `last_diff_path` after diff generation.

### Changed

- Internal scanner code was rebuilt to prepare for future safe migrations.
- Export payload version updated to `0.0.4`.
- Repository URLs point to `kimzeuner/Home-Assistant-Migration-Assistant`.

### Safety

- The integration remains read-only.
- No Home Assistant configuration files are modified.

## v0.0.3

### Added

- Service `ha_migration_assistant.export_plan`.
- JSON export to `/config/ha_migration_assistant/`.
- Attribute `last_export_path`.

## v0.0.2

### Added

- Service `ha_migration_assistant.rescan`.
- File summaries and richer scan attributes.
- Markdown migration plan attribute.

## v0.0.1

### Added

- Initial read-only migration scanner.
- Config flow and options flow.
- Basic sensors for matches and scanned files.
