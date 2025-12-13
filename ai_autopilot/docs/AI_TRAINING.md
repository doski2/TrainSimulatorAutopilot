# AI — Entrenamiento (visión general)

Este documento describe los pasos para entrenar un modelo base (baseline) para
clasificación de freno usando datasets grabados en formato JSONL.

1) Dataset: `record_session.py` registra snapshots en `data/sessions/*.jsonl`.
2) Etiquetado: `labeler.py` aplica reglas heurísticas simples (umbrales de
`TrainBrakeControl`) para generar etiquetas. 3) Preprocesado: `preprocess.py`
genera secuencias (ventanas temporales) para modelado secuencial. 4)
Entrenamiento: `train_model.py` entrena un LSTM pequeño y guarda el modelo como
`brake_model.h5`.

Características recomendadas y sugerencias:

- Usar estas señales principales: `CurrentSpeed_kmh`, `TrainBrakeControl`,
`BrakePipePressurePSI`, `TrainBrakeCylinderPressurePSI`, `RPM` y `Ammeter`.
- Ingeniería de features: añadir derivadas (deltas), medias móviles, y
transformaciones (ej. normalización por asset); `time-of-day` rara vez es
crítico para la detección de freno.
- Validación: usar `validation_split` y reservar un conjunto de test inalterado
para evaluación final.

Seguridad: definir umbrales y reglas de emergencia (siempre preferir
intervención humana cuando sea necesario).
