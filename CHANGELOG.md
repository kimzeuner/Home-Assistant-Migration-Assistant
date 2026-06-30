# Changelog

## v0.0.8

- Added service `ha_migration_assistant.create_backup`.
- Creates timestamped backups under `/config/ha_migration_assistant/backups/`.
- Writes a `backup_manifest.json` with copied and skipped files.
- Keeps the integration read-only: no original files are modified.
- Updated bundled transparent brand assets.

## v0.0.6

- Added registry-aware scanning.
- Added scanner options for `.storage` and backup folders.
- Improved internal scan result structure.

## v0.0.5

- Changed integration type from helper to service.
- Cleaned up integration labels and service metadata.

## v0.0.4

- Introduced modular scanner architecture.
- Added confidence scores and category summaries.
- Added `generate_diff` service.

## v0.0.3

- Added `export_plan` service.

## v0.0.2

- Added `rescan` service and richer match attributes.

## v0.0.1

- Initial read-only scanner.
