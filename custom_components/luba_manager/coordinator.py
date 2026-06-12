from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta
from .utils import base_score
from .const import ZONES

class LubaCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, config, options):
        super().__init__(
            hass,
            name="luba_manager",
            update_interval=timedelta(minutes=15),
        )

        self.config = config
        self.options = options

    async def _async_update_data(self):

        temp = float(self.hass.states.get("sensor.czujnik_ogrod_temperature").state or 0)

        rain = float(
            self.hass.states.get("weather.forecast_home")
            .attributes.get("precipitation_probability", 0)
        )

        last_zone = self.hass.states.get("input_text.luba_last_zone").state

        base = base_score(temp, rain)

        scores = {
            "front": base,
            "tyl": base + 5,
            "lacznik": base - 5,
            "bagno": base - 15,
        }

        for z in scores:
            if z == last_zone:
                scores[z] -= 20
            else:
                scores[z] += 10

        best = max(scores, key=scores.get)

        queue = sorted(scores, key=scores.get, reverse=True)[:2]

        return {
            "best": best,
            "queue": queue,
            "scores": scores
        }