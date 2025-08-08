## Metro de Santiago (Home Assistant)

Integración NO oficial para mostrar el estado de las líneas del Metro de Santiago en Home Assistant.

**Características**
- Sensores por línea (L1–L6) y sensor de resumen
- Estaciones afectadas como atributos
- Intervalo de actualización configurable desde la UI

**Instalación rápida (HACS)**
1. HACS → Integrations → + → *Custom repositories* → agrega `duvob90/metro-HA` (Integration)
2. Instala **Metro de Santiago** y reinicia
3. Settings → Devices & Services → Add Integration → **Metro de Santiago**

**Notas**
- Datos desde `https://api.xor.cl/red/metro-network` (no oficial). Usa intervalos ≥ 180 s.
