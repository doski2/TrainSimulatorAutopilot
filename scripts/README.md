# README - scripts/cleanup_persisted_fuel.py

Propósito:

- El script `cleanup_persisted_fuel.py` elimina las entradas históricas
  de alertas y los campos de combustible (`fuel*`) de los archivos
  persistentes `alerts.json` y `data/telemetry_history.json`.
- Crea respaldos con sufijo `.bak.YYYYMMDDTHHMMSSZ` antes de sobrescribir los
  archivos.

Uso:

1. Activar el virtualenv del proyecto.

```powershell
& .\.venv\Scripts\Activate.ps1
```

1. Ejecutar el script:

```powershell
# Usar el Python del virtualenv activo
python scripts/cleanup_persisted_fuel.py
```

Comportamiento:

- Si `alerts.json` contiene entradas con `alert_type` que comienzan con
  `fuel` o `alert_id` con prefijo `fuel_`, se mueven a la copia de backup y se
  resuelven (es decir, `alerts.json` queda actualizado sin esas entradas).
- Si `data/telemetry_history.json` tiene claves como `fuelLevel`, `fuel_level`
  o `fuelConsumption`, se eliminan dichas claves y se genera un backup del
  archivo.
- Si no se encuentran entradas a limpiar, se muestra un mensaje y no se
  alteran los archivos.

Reversión:

- Se conservan los respaldos en el mismo directorio con sufijo
  `.bak.YYYYMMDDTHHMMSSZ`. Restaurar manualmente si es necesario.

Seguridad:

- Ejecute el script en una copia de trabajo o en un entorno controlado si
  desea conservar datos históricos exactos.

Notas:

- El script está pensado para escenarios TSC donde `FuelLevel` se considera
  no implementado / infinito. No debe ejecutarse si su integración usa
  `FuelLevel` activamente.
