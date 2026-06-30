# Home Assistant Migration Assistant

A safe migration helper for Home Assistant.

Version `v0.0.3` is still intentionally read-only. It scans selected Home Assistant configuration files for usages of an old entity ID, creates a migration plan, and can export that plan as JSON.

## Current features

- Config flow UI
- Options flow UI
- Read-only scan
- Manual rescan service
- JSON migration plan export service
- Finds references in common YAML files
- Finds references in Lovelace storage files
- Creates sensors for:
  - match count
  - files with matches
  - scanned files
- Exposes file summaries and match context as entity attributes
- Exposes a Markdown migration plan as an entity attribute
- Stores exported plans under `/config/ha_migration_assistant/`

## Services

### `ha_migration_assistant.rescan`

Rescans configured migration entries.

```yaml
service: ha_migration_assistant.rescan
```

Optionally rescan one config entry by entry ID:

```yaml
service: ha_migration_assistant.rescan
data:
  entry_id: "YOUR_CONFIG_ENTRY_ID"
```

### `ha_migration_assistant.export_plan`

Exports the latest migration plan as JSON.

```yaml
service: ha_migration_assistant.export_plan
```

Optional filename:

```yaml
service: ha_migration_assistant.export_plan
data:
  filename: "living_room_switch_migration"
```

The file will be written to:

```text
/config/ha_migration_assistant/living_room_switch_migration.json
```

## Not implemented yet

- Writing changes to files
- Backup creation
- Full diff UI
- Multi-entity migration plans

## Installation during development

Copy this folder:

```text
custom_components/ha_migration_assistant
```

to:

```text
/config/custom_components/ha_migration_assistant
```

Restart Home Assistant and add the integration from **Settings > Devices & services > Add integration**.

## GitHub repository

Repository:

```text
https://github.com/kimzeuner/Home-Assistant-Migration-Assistant
```

Issue tracker:

```text
https://github.com/kimzeuner/Home-Assistant-Migration-Assistant/issues
```

## GitHub release workflow without command line

1. Upload/replace changed files in the GitHub repository.
2. Commit via the GitHub web UI.
3. Create a release named `v0.0.3`.

## Safety model

The project should always follow this workflow:

1. Scan
2. Show plan
3. Create backup
4. Show diff
5. Apply migration only after explicit confirmation

Version `v0.0.3` implements step 1, part of step 2, and JSON export of the read-only plan.
