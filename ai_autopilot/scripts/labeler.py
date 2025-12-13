r"""
labeler.py
Generates label files for supervised learning from JSONL recorded sessions.
Examples: determines whether 'brake applied' or 'brake released' events occurred.

Usage:
  python ai_autopilot\scripts\labeler.py --input data/sessions/session-*.jsonl --output data/labeled/

This is a starter template implementing heuristic rule-based labels.
"""

import argparse
import json
import os


def label_snapshot(snapshot):
    labels = {}
    controls = snapshot.get("controls", {})
    train_brake = float(controls.get("TrainBrakeControl", 0.0))
    # Heuristic rules
    labels["brake_applied"] = 1 if train_brake >= 0.1 else 0
    labels["brake_released"] = 1 if train_brake < 0.1 else 0
    labels["is_stopped"] = 1 if controls.get("CurrentSpeed_kmh", 0.0) < 0.5 else 0
    return labels


def process_file(infile, outdir):
    os.makedirs(outdir, exist_ok=True)
    basename = os.path.basename(infile)
    out_path = os.path.join(outdir, basename.replace(".jsonl", ".labeled.jsonl"))
    with open(infile, encoding="utf-8") as f_in, open(out_path, "w", encoding="utf-8") as f_out:
        for line in f_in:
            snapshot = json.loads(line)
            labels = label_snapshot(snapshot)
            snapshot["labels"] = labels
            f_out.write(json.dumps(snapshot, ensure_ascii=False) + "\n")
    print("Labeled file written to", out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="ai_autopilot/data/labeled")
    args = parser.parse_args()
    process_file(args.input, args.output)
