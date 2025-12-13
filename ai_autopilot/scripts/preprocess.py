"""
preprocess.py
Preprocessing script: converts labeled JSONL into dataset windows appropriate for sequence models
Outputs: numpy files or TFRecord
"""

import json

import numpy as np


def windowed_sequences(jsonl_path, window_size=20, stride=1):
    with open(jsonl_path, encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]
    controls = [line["controls"] for line in lines]
    X = []
    y = []
    for i in range(0, len(controls) - window_size, stride):
        w = controls[i : i + window_size]
        # feature vector: speed, brake, rpm, brakepipe etc.
        feat = [
            [c.get("CurrentSpeed_kmh", 0), c.get("TrainBrakeControl", 0), c.get("RPM", 0)]
            for c in w
        ]
        # label: whether brake will be released in next step
        next_label = (
            lines[i + window_size]["labels"]["brake_released"]
            if "labels" in lines[i + window_size]
            else 0
        )
        X.append(feat)
        y.append(next_label)
    X = np.array(X)
    y = np.array(y)
    return X, y


if __name__ == "__main__":
    print("Preprocessing template. Modify features and windows as needed.")
