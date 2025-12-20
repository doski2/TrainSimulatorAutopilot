# Preparación de Ruta de Trabajo para Pruebas en el Simulador

Esta guía describe los pasos para preparar una ruta de trabajo en Train Simulator para probar el sistema de autopiloto.

## Paso 1: Verificar Instalación del Simulador

Asegúrate de que Train Simulator esté instalado en la ubicación estándar:
- Ruta: `C:\Program Files (x86)\Steam\steamapps\common\RailWorks`

Si está en otra ubicación, ajusta los paths en los scripts.

## Paso 2: Crear Directorio de Plugins

El sistema usa el directorio `plugins` dentro de RailWorks para comunicación.

1. Navega a `C:\Program Files (x86)\Steam\steamapps\common\RailWorks`
2. Crea la carpeta `plugins` si no existe.

Nota: Como es Program Files, necesitarás permisos de administrador.

## Paso 3: Copiar Scripts Lua

Usa el script automatizado para copiar los archivos:

```bash
python prepare_simulator.py
```

Esto copiará `complete_autopilot_lua.lua` a `RailWorks/plugins/engineScript.lua` y creará archivos de estado necesarios.

### Copia Manual (si es necesario)
Si prefieres hacerlo manualmente:

- Copia `complete_autopilot_lua.lua` a `RailWorks/plugins/`
- Renómbralo a `engineScript.lua` si es necesario.

## Paso 4: Configurar el Sistema de Autopiloto

1. Asegúrate de que `config.ini` esté configurado correctamente:
   - Verifica `TSC_INTEGRATION` para host y port.
   - Ajusta `WEB_DASHBOARD` si es necesario.

2. Ejecuta el dashboard web:
   ```bash
   python web_dashboard.py
   ```

3. Abre el navegador en `http://localhost:5001`

## Paso 5: Seleccionar y Cargar una Ruta en el Simulador

1. Abre Train Simulator.
2. Selecciona una ruta de prueba (ej: una ruta simple como "Tutorial" o una ruta descargada).
3. Elige una locomotora compatible (verifica que tenga script Lua).
4. Inicia el escenario.

## Paso 6: Probar el Autopiloto

1. En el dashboard web, activa el autopiloto.
2. Monitorea los logs y telemetría.
3. Usa los controles del dashboard para ajustar velocidad, etc.

## Notas Adicionales

- Asegúrate de que el puerto 1435 esté abierto para TSC_INTEGRATION.
- Si hay problemas, verifica los logs en `logs/train_simulator_autopilot.log`.
- Para rutas específicas, puedes crear configuraciones personalizadas en `config.ini` duplicando secciones.

## Ruta Recomendada para Pruebas

- **Ruta**: "Great Western Main Line" o una ruta simple.
- **Locomotora**: BR Class 66 o similar con soporte Lua.

Si encuentras problemas, revisa la documentación en `DOCUMENTATION.md`.