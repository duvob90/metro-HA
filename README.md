# Metro de Santiago (Home Assistant Custom Integration)

**Integración NO oficial** para mostrar el estado de las líneas del **Metro de Santiago** en Home Assistant, basada en los datos públicos de `https://api.xor.cl/red/metro-network`.

> ⚠️ Disclaimer: No es una API oficial de Metro. La disponibilidad y formato pueden cambiar sin previo aviso.

## Características
- Sensores por línea: **L1, L2, L3, L4, L4A, L5, L6**.
- Sensor **resumen** con estado global de la red.
- Atributos con **estaciones afectadas** por línea.
- **Configurable** desde la UI (intervalo de actualización).

## Instalación

### Opción A: HACS (recomendado)
1. HACS → *Integrations* → **+** → *Custom repositories*.
2. Pega la URL del repo `duvob90/metro-HA`, categoría **Integration** → *Add*.
3. Instala **Metro de Santiago** y reinicia Home Assistant.
4. Ve a **Settings → Devices & Services → Add Integration** y busca **Metro de Santiago**.

### Opción B: Manual
1. Copia la carpeta `custom_components/metro_santiago/` dentro de tu carpeta `config/custom_components/`.
2. Reinicia Home Assistant.
3. Agrega la integración desde **Settings → Devices & Services → Add Integration**.

## Configuración
- **Scan interval (segundos):** cada cuánto se consultará la API (por defecto **180 s**). Sé prudente para no saturar el servicio.

## Entidades
- `sensor.metro_santiago_resumen` → valor: `Operativa` / `Con incidencias`
  - Atributo `detalle`: diccionario `{ "L1": [...estaciones...], "L2": [...] }` con estaciones afectadas por línea.
- `sensor.metro_línea_1` (nombre visible “Metro Línea 1”) → valor: `Operativa` / `Con incidencias`
  - Atributo `estaciones_afectadas`: lista de estaciones con incidencia.
- Análogamente para L2, L3, L4, L4A, L5, L6.

> Nota: los estados de estaciones provienen del campo `status` del servicio (`0 = operativa`, `!= 0 = algún tipo de afectación`).

## Ejemplos Lovelace

### Entities card
```yaml
type: entities
title: Estado Metro de Santiago
entities:
  - entity: sensor.metro_linea_1
    name: Línea 1
  - entity: sensor.metro_linea_2
    name: Línea 2
  - entity: sensor.metro_linea_3
    name: Línea 3
  - entity: sensor.metro_linea_4
    name: Línea 4
  - entity: sensor.metro_linea_4a
    name: Línea 4A
  - entity: sensor.metro_linea_5
    name: Línea 5
  - entity: sensor.metro_linea_6
    name: Línea 6
  - entity: sensor.metro_santiago_resumen
    name: Resumen
```

### Mushroom chips (colores por estado)
```yaml
type: custom:mushroom-template-card
icon: mdi:train
layout: vertical
multiline_secondary: true
# Color del ícono según si hay afectadas en alguna línea
icon_color: >
  {% set det = state_attr('sensor.metro_santiago_resumen','detalle') or {} %}
  {% set total = 0 %}
  {% for k,info in det.items() %}
    {% set total = total
      + (info.get('cerradas_temporalmente',[]) | length)
      + (info.get('no_habilitadas',[]) | length)
      + (info.get('accesos_cerrados',[]) | length)
    %}
  {% endfor %}
  {{ 'green' if total == 0 else 'red' }}
primary: Metro de Santiago
secondary: |
  {% set det = state_attr('sensor.metro_santiago_resumen','detalle') or {} %}
  {% set names = {'L1':'Línea 1','L2':'Línea 2','L3':'Línea 3','L4':'Línea 4','L4A':'Línea 4A','L5':'Línea 5','L6':'Línea 6'} %}
  {% set order = ['L1','L2','L3','L4','L4A','L5','L6'] %}
  {% set ns = namespace(out=[]) %}
  {% for ln in order %}
    {% set info = det.get(ln, {}) %}
    {% set cerradas = (info.get('cerradas_temporalmente',[]) | length)
                    + (info.get('no_habilitadas',[]) | length)
                    + (info.get('accesos_cerrados',[]) | length) %}
    {% set total = info.get('totales', 0) %}
    {% if total > 0 and cerradas == total %}
      {% set state = 'Cerrada' %}
    {% elif cerradas > 0 %}
      {% set state = 'Con incidencias (' ~ cerradas ~ ')' %}
    {% else %}
      {% set state = 'Operativa' %}
    {% endif %}
    {% set ns.out = ns.out + [ names[ln] ~ ' — ' ~ state ] %}
  {% endfor %}
  {{ ns.out | join('\n') }}

```

## Troubleshooting
- **No aparecen sensores**: revisa *Settings → System → Logs* (habilita debug abajo).
- **Errores de conexión**: verifica internet, firewall y que la URL de la API esté accesible.
- **Demasiadas consultas**: sube el `scan_interval` (p.ej., 300–600 s).

### Logger de depuración
En `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.metro_santiago: debug
```

## Desarrollo
- `custom_components/metro_santiago/` contiene el *custom component*.
- Usa *Reload* desde la UI (Developer Tools → YAML → *Restart* o *Reload* de integraciones) para probar cambios.
- PRs bienvenidos.

## Licencia
MIT © 2025 duvob90
