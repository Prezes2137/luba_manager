from homeassistant import config_entries

from .const import CONF_ZONE_COUNT, CONF_ZONES
from .flow_utils import (
    build_general_schema,
    build_zone_schema,
    build_zones,
    validate_zone_names,
)

class LubaOptionsFlow(config_entries.OptionsFlow):

    def __init__(self, entry):
        self.entry = entry
        self._general_data = {}
        self._zone_defaults = []

    async def async_step_init(self, user_input=None):

        defaults = {**self.entry.data, **self.entry.options}
        self._zone_defaults = defaults.get(CONF_ZONES, [])

        if user_input is not None:
            self._general_data = dict(user_input)
            return await self.async_step_zones()

        return self.async_show_form(step_id="init", data_schema=build_general_schema(defaults))

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
                return self.async_create_entry(title="", data=data)

        return self.async_show_form(
            step_id="zones",
            data_schema=build_zone_schema(zone_count, self._zone_defaults),
            errors=errors,
        )