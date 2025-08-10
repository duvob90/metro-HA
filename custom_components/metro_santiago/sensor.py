from __future__ import annotations
from typing import Any, List

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

def _line_data(coordinator, line_id: str) -> dict | None:
    data = coordinator.data or {}
    lines = data.get("lines", [])
    for ln in lines:
        if ln.get("id") == line_id:
            return ln
    return None

def _split_by_status(stations: List[dict[str, Any]]):
    """Separa estaciones por tipo de status según la API xorcl:
       0 operativa, 1 cerrada temporal, 2 no habilitada, 3 accesos cerrados."""
    oper = [s for s in stations if s.get("status", 0) == 0]
    closed_temp = [s for s in stations if s.get("status") == 1]
    not_enabled = [s for s in stations if s.get("status") == 2]
    access_closed = [s for s in stations if s.get("status") == 3]
    return oper, closed_temp, not_enabled, access_closed

class MetroLineSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, line_id: str):
        super().__init__(coordinator)
        self._line_id = line_id
        self._attr_unique_id = f"metro_santiago_{line_id.lower()}"
        self._attr_name = f"Metro {LINE_NAME.get(line_id, line_id)}"
        self._attr_icon = "mdi:subway-variant"

    @property
    def native_value(self) -> str:
        ln = _line_data(self.coordinator, self._line_id)
        if not ln:
            return "unknown"

        stations: List[dict[str, Any]] = ln.get("stations", [])
        if not stations:
            return "Sin datos"

        oper, closed_temp, not_enabled, access_closed = _split_by_status(stations)
        total = len(stations)
        closed_like = len(closed_temp) + len(not_enabled)

        # TODAS cerradas/no habilitadas -> Cerrada (típico fuera de horario)
        if closed_like == total:
            return "Cerrada"

        # Hay cierres o accesos cerrados, pero no es cierre total
        if closed_like > 0 or len(access_closed) > 0:
            # Si predominantemente hay accesos cerrados y casi todo operativo, dilo
            if len(access_closed) > 0 and closed_like == 0:
                return "Con accesos cerrados"
            return "Con incidencias"

        # Ninguna afectación
        return "Operativa"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        ln = _line_data(self.coordinator, self._line_id)
        if not ln:
            return {}
        stations: List[dict[str, Any]] = ln.get("stations", [])
        oper, closed_temp, not_enabled, access_closed = _split_by_status(stations)

        def names(lst): return [s.get("name") for s in lst]

        return {
            "operativas": names(oper),
            "cerradas_temporalmente": names(closed_temp),
            "no_habilitadas": names(not_enabled),
            "accesos_cerrados": names(access_closed),
            "totales": len(stations)
        }

class MetroSummarySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = "metro_santiago_resumen"
        self._attr_name = "Metro Santiago - Resumen"
        self._attr_icon = "mdi:train"

    @property
    def native_value(self) -> str:
        data = self.coordinator.data or {}
        lines = data.get("lines", [])
        total_closed_like = 0
        total_access_closed = 0
        for ln in lines:
            stations = ln.get("stations", [])
            _, ctemp, nena, acc = _split_by_status(stations)
            total_closed_like += len(ctemp) + len(nena)
            total_access_closed += len(acc)

        if total_closed_like == 0 and total_access_closed == 0:
            return "Operativa"
        # Si TODAS las estaciones están cerradas/no habilitadas en todas las líneas, opcionalmente podríamos mostrar “Cerrada”
        return "Con incidencias"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        detalle = {}
        for ln in data.get("lines", []):
            lid = ln.get("id")
            stations = ln.get("stations", [])
            oper, ctemp, nena, acc = _split_by_status(stations)

            detalle[lid] = {
                "operativas": [s.get("name") for s in oper],
                "cerradas_temporalmente": [s.get("name") for s in ctemp],
                "no_habilitadas": [s.get("name") for s in nena],
                "accesos_cerrados": [s.get("name") for s in acc],
                "totales": len(stations)
            }
        return {"detalle": detalle}
