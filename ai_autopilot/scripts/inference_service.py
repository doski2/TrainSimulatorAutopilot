"""
inference_service.py
Simple FastAPI service to read current `GetData.txt` snapshot,
perform normalization and run inference using the saved model.

Endpoint: POST /infer
Body: JSON of current snapshot
Response: Predicted action (e.g., brake_release probability)

This file is a starter template.
"""

import os
from typing import Any

try:
    import uvicorn  # type: ignore[import]
except Exception:  # pragma: no cover - optional dependency in dev environments
    uvicorn = None  # type: ignore[assignment]

try:
    from fastapi import FastAPI, HTTPException  # type: ignore[import]
except Exception:  # pragma: no cover - ensure helpful error
    FastAPI = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[assignment]

app: Any = FastAPI() if FastAPI is not None else None

# load model - placeholder
MODEL_PATH = "ai_autopilot/models/brake_model.h5"

# model holder
model: Any = None


if app is not None:

    @app.on_event("startup")
    def load_model_event():
        # import tensorflow and keras explicitly to help some linters/Pylance
        try:
            from tensorflow import keras  # type: ignore[import]
        except Exception:  # pragma: no cover - optional on dev envs
            keras: Any = None  # type: ignore[assignment]

        global model
        if os.path.exists(MODEL_PATH) and keras is not None:
            model = keras.models.load_model(MODEL_PATH)
        else:
            model = None


if app is not None:

    @app.post("/infer")
    def infer(payload: dict):
        global model
        if model is None:
            if HTTPException is not None:
                raise HTTPException(status_code=503, detail="Model not loaded")
            raise RuntimeError("Model not loaded")
        # flatten payload features - placeholder conversion
        features = payload.get("features")
        import numpy as np

        x = np.array([features])
        pred = model.predict(x)
        return {"pred": float(pred[0][0])}


if __name__ == "__main__" and uvicorn is not None and app is not None:
    uvicorn.run(app, host="127.0.0.1", port=8000)
