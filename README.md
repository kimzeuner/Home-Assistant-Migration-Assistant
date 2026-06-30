![GitHub Release](https://img.shields.io/github/v/release/kimzeuner/Home-Assistant-Migration-Assistant)
![HACS](https://img.shields.io/badge/HACS-Default-blue.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025.7+-41BDF5.svg)
![License](https://img.shields.io/github/license/kimzeuner/Home-Assistant-Migration-Assistant)

# Home Assistant Migration Assistant

A custom Home Assistant integration that helps you migrate entity references safely.

The assistant scans your Home Assistant configuration for references to an old entity ID and prepares a migration plan for a new entity ID. It is designed to be safe first: the current release is still read-only and does not modify your configuration files.

## Repository

- Repository: https://github.com/kimzeuner/Home-Assistant-Migration-Assistant
- Issues: https://github.com/kimzeuner/Home-Assistant-Migration-Assistant/issues

## v0.0.5 highlights

- Changes the manifest `integration_type` from `helper` to `service` so Home Assistant treats the integration as a service-style integration instead of sending users to the Helpers page.
- Keeps all v0.0.4 scanner, report, export, and diff functionality.
- Adds service icons via `icons.json`.
- Adds local brand asset support in `custom_components/ha_migration_assistant/brand/` for Home Assistant 2026.3 and newer.
- Updates config-flow descriptions and export metadata to `0.0.5`.

## Features

- Scan for references to an old entity ID.
- Compare them against a planned new entity ID.
- Categorize matches by source type, for example automations, scripts, scenes, Lovelace, blueprints, templates, `.storage`, and general config files.
- Include confidence scores for each match.
- Expose scan summary sensors.
- Export a JSON migration plan.
- Generate a read-only diff preview.

## Services

### `ha_migration_assistant.rescan`

Rescans configured migration plans.

Optional fields:

- `entry_id`

### `ha_migration_assistant.export_plan`

Exports the current migration plan as JSON to:

```text
/config/ha_migration_assistant/
```

Optional fields:

- `entry_id`
- `filename`

### `ha_migration_assistant.generate_diff`

Generates a read-only `.diff` preview in:

```text
/config/ha_migration_assistant/
```

Optional fields:

- `entry_id`
- `filename`

## Installation

Copy the integration folder to your Home Assistant config directory:

```text
custom_components/ha_migration_assistant
```

Restart Home Assistant and add the integration from **Settings → Devices & services → Add integration**.

## Safety status

Current release: **read-only**.

This integration scans, reports, exports plans, and generates diffs. It does not apply migrations yet.

