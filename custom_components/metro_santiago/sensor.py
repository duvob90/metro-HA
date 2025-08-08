from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, LINES

LINE_NAME = {
    "L1": "Línea 1", "L2": "Línea 2", "L3": "Línea 3",
    "L4": "Línea 4", "L4A": "Línea 4A", "L5": "Línea 5", "L6": "Línea 6"
}

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    ents = []
    for lid in LINES:
        ents.append(MetroLineSensor(coordinator, lid))
    ents.append(MetroSummarySensor(coordinator))
    async_add_entities(ents, True)

def _line_data(coordinator, line_id):
    data = coordinator.data or {}
    lines = data.get("lines", [])
    for ln in lines:
        if ln.get("id") == line_id:
            return ln
    return None

class MetroLineSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, line_id):
        super().__init__(coordinator)
        self._line_id = line_id
        self._attr_unique_id = f"metro_santiago_{line_id.lower()}"
        self._attr_name = f"Metro {LINE_NAME.get(line_id,line_id)}"
        self._attr_icon = "mdi:subway-variant"

    @property
    def native_value(self):
        ln = _line_data(self.coordinator, self._line_id)
        if not ln:
            return "unknown"
        stations = ln.get("stations", [])
        affected = [s for s in stations if s.get("status", 0) != 0]
        return "Operativa" if len(affected) == 0 else "Con incidencias"

    @property
    def extra_state_attributes(self):
        ln = _line_data(self.coordinator, self._line_id)
        if not ln:
            return {}
        affected = [s.get("name") for s in ln.get("stations", []) if s.get("status", 0) != 0]
        return {"estaciones_afectadas": affected}

class MetroSummarySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = "metro_santiago_resumen"
        self._attr_name = "Metro Santiago - Resumen"
        self._attr_icon = "mdi:train"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        lines = data.get("lines", [])
        total_affected = 0
        for ln in lines:
            total_affected += len([s for s in ln.get("stations", []) if s.get("status", 0) != 0])
        return "Operativa" if total_affected == 0 else "Con incidencias"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        out = {}
        for ln in data.get("lines", []):
            lid = ln.get("id")
            aff = [s.get("name") for s in ln.get("stations", []) if s.get("status", 0) != 0]
            out[lid] = aff
        return {"detalle": out}
