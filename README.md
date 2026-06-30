# Home Assistant Migration Assistant

![GitHub Release](https://img.shields.io/github/v/release/kimzeuner/Home-Assistant-Migration-Assistant)
![License](https://img.shields.io/github/license/kimzeuner/Home-Assistant-Migration-Assistant)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.6%2B-41BDF5.svg)

A read-only migration planning tool for Home Assistant entity replacements.

## What it does

The integration helps you plan the replacement of one entity ID with another one, for example:

```text
switch.old -> switch.new
```

It scans your Home Assistant configuration and reports where the old entity is referenced.

## Current status

Version `v0.0.6` is still read-only. It does not modify your configuration.

## Features

- Config Flow based setup
- Options Flow
- Entity Registry awareness
- File-system scanner
- Scanner categories for automations, scripts, scenes, groups, templates, Lovelace, `.storage`, blueprints, and generic config
- Confidence score per match
- Markdown report attribute
- JSON and Markdown export service
- Unified diff preview service

## Services

### `ha_migration_assistant.rescan`

Runs the scanner again.

### `ha_migration_assistant.export_plan`

Exports a JSON and Markdown migration plan to:

```text
/config/ha_migration_assistant/
```

### `ha_migration_assistant.generate_diff`

Generates a read-only `.diff` preview in:

```text
/config/ha_migration_assistant/
```

## Installation

Copy:

```text
custom_components/ha_migration_assistant
```

to:

```text
/config/custom_components/ha_migration_assistant
```

Restart Home Assistant and add the integration from **Settings > Devices & services**.

## Repository

https://github.com/kimzeuner/Home-Assistant-Migration-Assistant

## Issues

https://github.com/kimzeuner/Home-Assistant-Migration-Assistant/issues
