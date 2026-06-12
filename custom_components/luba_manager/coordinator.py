from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta
from .utils import base_score
from .const import (
    CONF_MOWER_ENTITY_ID,
    CONF_ZONE_AREA,
    CONF_ZONE_DRYING_SPEED,
    CONF_ZONE_ID,
    CONF_ZONE_NAME,
    CONF_ZONES,
)


def _normalize_key(value):
    return str(value or "").strip().casefold().replace(" ", "_")


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

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

        temperature_state = self.hass.states.get("sensor.czujnik_ogrod_temperature")
        temp = _safe_float(temperature_state.state if temperature_state else None)

        weather_state = self.hass.states.get("weather.forecast_home")
        rain = _safe_float(weather_state.attributes.get("precipitation_probability", 0) if weather_state else None)

        last_zone_state = self.hass.states.get("input_text.luba_last_zone")
        last_zone = _normalize_key(last_zone_state.state if last_zone_state else "")

        base = base_score(temp, rain)

        zones = self.config.get(CONF_ZONES, []) or self.options.get(CONF_ZONES, [])
        scores = {}
        zone_names = {}

        for zone in zones:
            zone_id = zone.get(CONF_ZONE_ID) or _normalize_key(zone.get(CONF_ZONE_NAME))
            zone_name = zone.get(CONF_ZONE_NAME) or zone_id
            area = _safe_float(zone.get(CONF_ZONE_AREA, 0))
            drying_speed = _safe_float(zone.get(CONF_ZONE_DRYING_SPEED, 0))

            score = base
            score += min(area / 50.0, 20)
            score += drying_speed * 3

            if last_zone and last_zone in {zone_id, _normalize_key(zone_name)}:
                score -= 20
            else:
                score += 10

            scores[zone_id] = score
            zone_names[zone_id] = zone_name

        best_zone_id = max(scores, key=scores.get) if scores else None
        queue_ids = sorted(scores, key=scores.get, reverse=True)[:2] if scores else []

        return {
            "best": zone_names.get(best_zone_id, best_zone_id),
            "best_zone_id": best_zone_id,
            "mower_entity_id": self.config.get(CONF_MOWER_ENTITY_ID),
            "queue": [zone_names.get(zone_id, zone_id) for zone_id in queue_ids],
            "scores": scores,
            "zones": zones,
        }