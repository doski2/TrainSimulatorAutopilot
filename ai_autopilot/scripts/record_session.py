"""
record_session.py
Script to read `GetData.txt` and generate normalized JSONL snapshots for AI training.

Usage:
    & .\\.venv\\Scripts\\Activate.ps1
    python ai_autopilot\\scripts\record_session.py --output data/sessions/session-<timestamp>.jsonl

This file is a starter template and includes examples of reading GetData.txt and writing JSONL.
"""

import json
import os
import time
from datetime import datetime

DATA_FILE = r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt"

OUTPUT_DEFAULT = rf"ai_autopilot/data/sessions/session-{int(time.time())}.jsonl"


def parse_getdata(lines):
    # parse GetData.txt format into a dict (ControlName -> ControlValue)
    data = {}
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("ControlName:"):
            key = line.split(":", 1)[1].strip()
            # find ControlValue
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("ControlValue:"):
                j += 1
            if j < len(lines):
                value = lines[j].strip().split(":", 1)[1].strip()
                try:
                    v = float(value)
                except ValueError:
                    v = value
                data[key] = v
        i += 1
    return data


def normalize_snapshot(raw, timestamp=None, asset_name=None):
    # Convert to normalized schema (example)
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat() + "Z"
    snapshot = {"timestamp": timestamp, "asset_name": asset_name, "engine_index": 0, "controls": {}}
    # Example normalizations
    if "CurrentSpeed" in raw:
        # convert m/s to km/h
        try:
            speed_kmh = abs(float(raw["CurrentSpeed"])) * 3.6
        except Exception:
            speed_kmh = 0.0
        snapshot["controls"]["CurrentSpeed_kmh"] = round(speed_kmh, 3)
    if "RPM" in raw:
        try:
            snapshot["controls"]["RPM"] = float(raw["RPM"])
        except Exception:
            snapshot["controls"]["RPM"] = 0.0
    if "TrainBrakeControl" in raw:
        snapshot["controls"]["TrainBrakeControl"] = float(raw["TrainBrakeControl"])
    # Copy other fields if exist
    for k in ["Ammeter", "Wheelslip", "AirBrakePipePressurePSI", "TrainBrakeCylinderPressurePSI"]:
        if k in raw:
            try:
                snapshot["controls"][k] = float(raw[k])
            except Exception:
                snapshot["controls"][k] = raw[k]

    return snapshot


if __name__ == "__main__":
    output = OUTPUT_DEFAULT
    os.makedirs(os.path.dirname(output), exist_ok=True)
    print("Recording AI snapshots to:", output)
    with open(output, "w", encoding="utf-8") as out_f:
        # Simple loop - read snapshots every 500ms
        try:
            while True:
                if not os.path.exists(DATA_FILE):
                    time.sleep(1)
                    continue
                with open(DATA_FILE, encoding="utf-8") as f:
                    lines = f.readlines()
                raw = parse_getdata(lines)
                snapshot = normalize_snapshot(raw)
                out_f.write(json.dumps(snapshot, ensure_ascii=False) + "\n")
                out_f.flush()
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("Stopped recording.")
