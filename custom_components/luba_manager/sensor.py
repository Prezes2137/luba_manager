from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LubaBestSensor(coordinator, entry.entry_id)])


class LubaBestSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_best_zone"
        self._attr_name = "Luba Best Zone"
        self._attr_icon = "mdi:robot-mower"

    @property
    def native_value(self):
        return self.coordinator.data.get("best")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return {
            "best_id": data.get("best_zone_id"),
            "queue": data.get("queue", []),
            "scores": data.get("scores", {}),
            "mower_entity_id": data.get("mower_entity_id"),
            "zones": data.get("zones", []),
        }