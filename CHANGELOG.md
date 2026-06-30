# Changelog

## v0.0.3

- Added `ha_migration_assistant.export_plan` service.
- Exported read-only migration plans are written as JSON under `/config/ha_migration_assistant/`.
- Added `last_export_path` attribute after exporting a plan.
- Updated project metadata to use the `kimzeuner/Home-Assistant-Migration-Assistant` repository URLs.
- Kept the integration read-only; no configuration files are modified.

## v0.0.2

- Added `ha_migration_assistant.rescan` service.
- Added additional sensor for files with matches.
- Added file summaries and match context as entity attributes.
- Added Markdown migration plan as entity attribute.
- Improved README documentation.

## v0.0.1

- Initial read-only MVP.
- Added config flow and options flow.
- Added scanner for common Home Assistant YAML and Lovelace storage files.
- Added sensors for match count and scanned files.
