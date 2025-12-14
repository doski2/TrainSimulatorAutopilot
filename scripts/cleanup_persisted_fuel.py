#!/usr/bin/env python3
"""
Cleanup script: remove historical fuel alerts and fuel fields from persisted telemetry.
Creates backups with .bak timestamp.
"""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALERTS_FILE = ROOT / "alerts.json"
TELEMETRY_FILE = ROOT / "data" / "telemetry_history.json"

BACKUP_SUFFIX = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

FUEL_ALERT_TYPES = {"fuel_low", "fuel_high", "fuel"}
FUEL_FIELD_KEYS = {"fuel_level", "fuelLevel", "fuelConsumption", "combustible", "combustible_porcentaje", "combustible_galones"}



def cleanup_alerts(path: Path) -> None:
    if not path.exists():
        print(f"No alerts file at {path}")
        return
    with path.open("r", encoding="utf-8-sig") as f:
        alerts = json.load(f)

    original_len = len(alerts)

    cleaned = [a for a in alerts if not (str(a.get("alert_type", "")).lower().startswith("fuel") or "fuel_" in str(a.get("alert_id", "")).lower())]

    removed = original_len - len(cleaned)
    if removed == 0:
        print("No fuel alert entries to remove.")
        return

    backup = path.with_suffix(path.suffix + ".bak." + BACKUP_SUFFIX)
    path.rename(backup)

    with path.open("w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)

    print(f"Backed up alerts to {backup} and removed {removed} fuel alerts.")


def cleanup_telemetry(path: Path) -> None:
    if not path.exists():
        print(f"No telemetry file at {path}")
        return
    with path.open("r", encoding="utf-8-sig") as f:
        telemetry = json.load(f)

    count_items = len(telemetry)
    removed_fields = 0

    for item in telemetry:
        if not isinstance(item, dict):
            continue
        data = item.get("data")
        if not isinstance(data, dict):
            continue
        for k in list(data.keys()):
            if k in FUEL_FIELD_KEYS:
                del data[k]
                removed_fields += 1

    if removed_fields == 0:
        print("No fuel fields found in telemetry history.")
        return

    backup = path.with_suffix(path.suffix + ".bak." + BACKUP_SUFFIX)
    path.rename(backup)

    with path.open("w", encoding="utf-8") as f:
        json.dump(telemetry, f, indent=2, ensure_ascii=False)

    print(f"Backed up telemetry to {backup} and removed {removed_fields} fuel fields from {count_items} telemetry entries.")


if __name__ == "__main__":
    print("Starting fuel cleanup...")
    cleanup_alerts(ALERTS_FILE)
    cleanup_telemetry(TELEMETRY_FILE)
    print("Done.")
