# AI Autopilot — TrainSimulatorAutopilot

## Overview

Este módulo `ai_autopilot` contiene artefactos, scripts y documentación para
integrar una IA de autopilot con Train Simulator Classic (TSC). Utiliza la
telemetría disponible en `GetData.txt` y los datos/alias de `debug.txt` y
`FullEngineData`.

## Estructura (carpeta)

- `ai_autopilot/`
  - `data/`    — JSONL snapshots and dataset files
  - `models/`  — Model checkpoints and exported models
  - `scripts/` — Collection, labelling, preprocessing and training scripts
  - `docs/`    — Documentation and diagrams
  - `tests/`   — Unit / integration tests for the pipeline
  - `README.md` — Este archivo
  - `requirements-ai.txt` — Requisitos Python para el módulo AI

## Objetivos inmediatos

1. Permitir recolección de datos (snapshots) normalizados en JSONL con metadatos
  comunes: timestamp, asset, engine index y sample index.
2. Implementar un etiquetador por heurística (rules-based) para extraer eventos de
  frenado y liberación.
3. Crear pipelines de preprocesamiento (normalización y generación de ventanas
  temporales) y dataset splits (train/val/test).
4. Entrenar un modelo baseline (LSTM/TCN) para predecir la intención de freno: "apli-
  car" / "liberar" o regresión para un valor suave de freno.
5. Implementar servicio de inferencia (FastAPI) que lea `GetData.txt`, normalice
  la entrada, ejecute el modelo y publique comandos seguros en `SendCommand.txt`.

## Requisitos previos (setup)

- Activar entorno virtual en el repo:

```powershell
& .\.venv\Scripts\Activate.ps1
pip install -r requirements-ai.txt
```

- `requirements-ai.txt` incluye (ejemplos):
  - `pandas`
  - `numpy`
  - `scikit-learn`
  - `tensorflow` (o `pytorch`)
  - `fastapi`, `uvicorn`, `pydantic`, `pytest`

## Esquema JSONL propuesto

Cada snapshot en `data/` será una línea JSON con este formato:

```json
{
  "timestamp": "2025-12-07T12:00:00Z",
  "asset_name": "BR204PACK01",
  "engine_index": 0,
  "sample_index": 12345,
  "controls": {
    "CurrentSpeed_kmh": 45.3,
    "Acceleration_m_s2": 0.12,
    "TrainBrakeControl": 0.44,
    "BrakePipe_Pa": 441000,
    "TrainBrakeCylinder_Pa": 448000,
    "RPM": 467.5,
    "Ammeter_amps": -12.5
  }
}
```

## Recomendaciones para recolección y normalización

- Convertir todas las unidades a un esquema único (Speed: km/h, Pressure: Pa o PSI,
  Current: Amps).
- Añadir campos `AssetName` y `EngineIndex` para poder agrupar o adaptar modelos
  por asset/locomotora.
- Guardar secuencias temporales en JSONL por sesión para usar en entrenamientos de
  series temporales.

## Etiqueta de freno (ejemplos heurísticos)

- `brake_applied`: TrainBrakeControl >= 0.1
- `brake_released`: TrainBrakeControl < 0.1
- `is_stopped`: CurrentSpeed_kmh < 0.1 durante 3 segundos

## Diseño de scripts (básico)

- `scripts/record_session.py`:
  - Monitorea `GetData.txt` y `debug.txt` y escribe snapshots normalizados en
    `data/sessions/<timestamp>.jsonl`.

- `scripts/labeler.py`:
  - Lee JSONL de sesiones, aplica reglas heurísticas para generar `label` (brake
    applied / released) y produce los ficheros en `data/labeled/`.

- `scripts/preprocess.py`:
  - Convierte datos a ventanas de timesteps, extrae features y guarda datasets en
    `data/dataset/`.

- `scripts/train_model.py`:
  - Entrenamiento (LSTM/TCN) con Keras/TensorFlow; guarda checkpoints en `models/`.

- `scripts/inference_service.py`:
  - Servicio FastAPI que consume `GetData.txt`, normaliza la entrada, ejecuta el
    modelo y, si la predicción está dentro de rangos seguros, escribe `SendCommand.txt`
    y graba un log en `SendCommandDebug.txt`.

- `tests/`:
  - `test_record_session.py`, `test_labeler.py`, `test_preprocess.py` y
    `test_inference_service.py`.

## Seguridad y validación (runtime)

- Implementar validaciones para evitar comandos fuera de rango, acciones que con-
  travengan reglas de seguridad y límites de cambio por segundo.
- Hacer "pair" con override humano: si el operador toma control, la IA no debe
  enviar comandos.

## Siguientes pasos (inmediatos)

1. Crear los stubs de los scripts y un `requirements-ai.txt` con dependencias.
2. Implementar `record_session.py` para la recolección y normalización (siguiente
  paso práctico si lo apruebas).

## Documentation (en detalle)

`docs/README_COLLECTION.md` — procedimientos de recolección y ejemplos de
línea JSONL.
`docs/AI_TRAINING.md` — preprocesado, features, arquitectura recomendada y
métricas.
`docs/INFERENCE.md` — cómo ejecutar el servicio, tuning de seguridad y
endpoints API.

¿Te parece si creo ahora los `_stubs_` de scripts y el `requirements-ai.txt`, y luego
continúo con `record_session.py`?

Si quieres que empiece ya con `record_session.py` y `labeler.py`, dímelo y los
genero con un README en `docs/` que incluya instrucciones paso a paso y comandos
de PowerShell para ejecución y pruebas.
