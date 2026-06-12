from homeassistant.helpers.entity import Entity

class LubaBestSensor(Entity):

    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def name(self):
        return "Luba Best Zone"

    @property
    def state(self):
        return self.coordinator.data.get("best")

    @property
    def icon(self):
        return "mdi:robot-mower"