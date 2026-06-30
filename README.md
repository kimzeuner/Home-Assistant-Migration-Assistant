# Home Assistant Migration Assistant

A Home Assistant custom integration for safely planning entity migrations.

It helps you find where an old entity ID is used, plan the replacement, generate a diff preview, and create backups before any future migration step.

> Current status: read-only. Version `v0.0.8` does not modify your Home Assistant configuration.

## Features

- Scan Home Assistant configuration files for an old entity ID.
- Compare old and new entities against the Entity Registry.
- Categorize matches by area such as automations, scripts, scenes, Lovelace, `.storage`, blueprints, templates, and config files.
- Generate a JSON/Markdown migration plan.
- Generate a unified diff preview.
- Create timestamped backups of affected files.

## Services

### `ha_migration_assistant.rescan`

Runs the scanner again for all configured migration plans.

### `ha_migration_assistant.export_plan`

Exports the current migration plan to:

```text
/config/ha_migration_assistant/
```

### `ha_migration_assistant.generate_diff`

Generates a read-only `.diff` preview in:

```text
/config/ha_migration_assistant/
```

### `ha_migration_assistant.create_backup`

Copies all files referenced by the current migration plan to:

```text
/config/ha_migration_assistant/backups/
```

The service also writes a `backup_manifest.json`. Original files are not changed.

## Installation

Copy this folder into your Home Assistant config directory:

```text
custom_components/ha_migration_assistant
```

Restart Home Assistant and add **Home Assistant Migration Assistant** from **Settings → Devices & services**.

## Repository

- Repository: https://github.com/kimzeuner/Home-Assistant-Migration-Assistant
- Issues: https://github.com/kimzeuner/Home-Assistant-Migration-Assistant/issues

## License

MIT
