from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_ZONE_COUNT, CONF_ZONES
from .flow_utils import (
    build_general_schema,
    build_zone_schema,
    build_zones,
    validate_zone_names,
)

class LubaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    def __init__(self):
        self._general_data = {}
        self._zone_defaults = []

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        from .options_flow import LubaOptionsFlow

        return LubaOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._general_data = dict(user_input)
            return await self.async_step_zones()

        return self.async_show_form(step_id="user", data_schema=build_general_schema({}))

    async def async_step_zones(self, user_input=None):
        errors = {}
        zone_count = self._general_data[CONF_ZONE_COUNT]

        if user_input is not None:
            zones = build_zones(user_input, zone_count)
            self._zone_defaults = zones
            if not validate_zone_names(zones):
                errors["base"] = "duplicate_zone_names"
            else:
                data = dict(self._general_data)
                data[CONF_ZONES] = zones
                return self.async_create_entry(title="Luba Manager", data=data)

        return self.async_show_form(
            step_id="zones",
            data_schema=build_zone_schema(zone_count, self._zone_defaults),
            errors=errors,
        )