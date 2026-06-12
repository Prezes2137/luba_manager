from homeassistant import config_entries

from .const import CONF_ZONES
from .flow_utils import build_schema, build_zones, validate_zone_names

class LubaOptionsFlow(config_entries.OptionsFlow):

    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):

        defaults = {**self.entry.data, **self.entry.options}
        errors = {}

        if user_input is not None:
            zones = build_zones(user_input)

            if not validate_zone_names(zones):
                errors["base"] = "duplicate_zone_names"
            else:
                data = {
                    key: value
                    for key, value in user_input.items()
                    if not key.startswith("zone_")
                }
                data[CONF_ZONES] = zones

                return self.async_create_entry(title="", data=data)

        return self.async_show_form(
            step_id="init",
            data_schema=build_schema(defaults),
            errors=errors,
        )