from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_NEW_ENTITY_ID,
    CONF_OLD_ENTITY_ID,
    CONF_SCAN_BACKUPS,
    CONF_SCAN_STORAGE,
    DEFAULT_SCAN_BACKUPS,
    DEFAULT_SCAN_STORAGE,
    DOMAIN,
)


class MigrationAssistantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            old_entity_id = user_input[CONF_OLD_ENTITY_ID].strip()
            new_entity_id = user_input[CONF_NEW_ENTITY_ID].strip()
            if "." not in old_entity_id:
                errors[CONF_OLD_ENTITY_ID] = "invalid_entity_id"
            elif "." not in new_entity_id:
                errors[CONF_NEW_ENTITY_ID] = "invalid_entity_id"
            else:
                await self.async_set_unique_id(f"{old_entity_id}->{new_entity_id}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"{old_entity_id} → {new_entity_id}",
                    data={
                        CONF_OLD_ENTITY_ID: old_entity_id,
                        CONF_NEW_ENTITY_ID: new_entity_id,
                    },
                    options={
                        CONF_SCAN_STORAGE: DEFAULT_SCAN_STORAGE,
                        CONF_SCAN_BACKUPS: DEFAULT_SCAN_BACKUPS,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_OLD_ENTITY_ID): str,
                    vol.Required(CONF_NEW_ENTITY_ID): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MigrationAssistantOptionsFlow(config_entry)


class MigrationAssistantOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_STORAGE,
                        default=options.get(CONF_SCAN_STORAGE, DEFAULT_SCAN_STORAGE),
                    ): bool,
                    vol.Required(
                        CONF_SCAN_BACKUPS,
                        default=options.get(CONF_SCAN_BACKUPS, DEFAULT_SCAN_BACKUPS),
                    ): bool,
                }
            ),
        )
