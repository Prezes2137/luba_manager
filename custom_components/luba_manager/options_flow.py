import voluptuous as vol
from homeassistant import config_entries

class LubaOptionsFlow(config_entries.OptionsFlow):

    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            "front_action": str,
            "tyl_action": str,
            "lacznik_action": str,
            "bagno_action": str,
        })

        return self.async_show_form(step_id="init", data_schema=schema)