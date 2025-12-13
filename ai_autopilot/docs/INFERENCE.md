
# Servicio de inferencia (FastAPI)

- Ejecutar el servidor del modelo:

```powershell
& .\.venv\Scripts\Activate.ps1
python ai_autopilot\scripts\inference_service.py
```

- Enviar POST a `/infer` con body JSON: `{"features": [[velocidad, freno, rpm,
  ...], ...]}` y recibirás la probabilidad o predicción del modelo.

- Mapear la probabilidad a comandos usando `tsc_integration.mapeo_comandos`, y
  escribir en `SendCommand.txt` el comando mapeado.

- Seguridad: aplicar filtros/clamps a los valores, rate-limiter y comprobaciones
  de sentido común (por ejemplo: si el modelo sugiere "liberar freno" pero
  `CurrentSpeed_kmh > 100`, bloquear y registrar la acción).
