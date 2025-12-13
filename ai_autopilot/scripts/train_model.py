"""
train_model.py
Baseline model training (LSTM) for brake classification.

Usage:
  python ai_autopilot\\scripts\train_model.py --data data/labeled/xxx.labeled.jsonl

"""

import argparse
import os
from typing import Any

try:
    from tensorflow.keras.callbacks import ModelCheckpoint  # type: ignore[import]
    from tensorflow.keras.layers import LSTM, Dense  # type: ignore[import]
    from tensorflow.keras.models import Sequential  # type: ignore[import]
    _TF_AVAILABLE = True
except Exception:  # pragma: no cover - Optional on dev envs
    ModelCheckpoint = Any  # type: ignore[assignment]
    LSTM = Any  # type: ignore[assignment]
    Dense = Any  # type: ignore[assignment]
    Sequential = Any  # type: ignore[assignment]
    _TF_AVAILABLE = False

from ai_autopilot.scripts.preprocess import windowed_sequences


def build_model(input_shape):
    if not _TF_AVAILABLE:
        raise RuntimeError("TensorFlow is required to build model. Install tensorflow to use this script.")
    model = Sequential()  # type: ignore[call-arg]
    model.add(LSTM(32, input_shape=input_shape))  # type: ignore[call-arg]
    model.add(Dense(16, activation="relu"))  # type: ignore[call-arg]
    model.add(Dense(1, activation="sigmoid"))  # type: ignore[call-arg]
    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])  # type: ignore
    return model


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--out", default="ai_autopilot/models")
    args = parser.parse_args()

    if not _TF_AVAILABLE:
        raise RuntimeError(
            "TensorFlow not available. Install tensorflow to train models: python -m pip install tensorflow"
        )
    os.makedirs(args.out, exist_ok=True)
    X, y = windowed_sequences(args.data)
    # X shape: (N, window, features)
    print("Train shapes", X.shape, y.shape)

    model = build_model((X.shape[1], X.shape[2]))
    ckpt = os.path.join(args.out, "brake_model.h5")
    model.fit(
        X,
        y,
        epochs=args.epochs,
        batch_size=32,
        validation_split=0.2,
        callbacks=[ModelCheckpoint(ckpt)],  # type: ignore[arg-type]
    )
    model.save(ckpt)
    print("Model saved to", ckpt)
