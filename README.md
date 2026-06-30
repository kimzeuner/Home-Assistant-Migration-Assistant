# Home Assistant Migration Assistant

A safe migration helper for Home Assistant.

Version `v0.0.1` is intentionally read-only. It scans selected Home Assistant configuration files for usages of an old entity ID and creates a migration plan for replacing it with a new entity ID.

## Current features

- Config flow UI
- Options flow UI
- Read-only scan
- Finds references in common YAML files
- Finds references in Lovelace storage files
- Creates sensors with match count and scanned file count
- Exposes the first matches as entity attributes

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

## GitHub setup without command line

1. Create a new GitHub repository named `ha-migration-assistant`.
2. Do not create a README, license or `.gitignore` on GitHub.
3. Upload all files from this project into the empty repository.
4. Replace `YOUR_GITHUB_USERNAME` in `manifest.json`.
5. Commit via the GitHub web UI.
6. Create a release named `v0.0.1`.

## GitHub setup with command line

```bash
git init
git add .
git commit -m "Initial v0.0.1"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ha-migration-assistant.git
git push -u origin main
git tag v0.0.1
git push origin v0.0.1
```

## Safety model

The project should always follow this workflow:

1. Scan
2. Show plan
3. Create backup
4. Show diff
5. Apply migration only after explicit confirmation

Version `v0.0.1` only implements step 1 and part of step 2.
