import json
from pathlib import Path

alerts_path = Path(__file__).parent.parent / "alerts.json"
minimal = [
    {
        "alert_id": "wheelslip_example_ack_20251214_214237",
        "alert_type": "wheelslip",
        "severity": "high",
        "title": "Deslizamiento de Ruedas (ejemplo)",
        "message": "Deslizamiento: 1.00 (umbral: 0.5)",
        "timestamp": "2025-12-14T21:42:37.035443",
        "data": {"wheelslip": 1.0, "threshold": 0.5, "slip_amount": 0.5},
        "acknowledged": True,
        "acknowledged_at": "2025-12-14T21:42:57.741013",
    },
    {
        "alert_id": "wheelslip_example_unack_20251203_004027",
        "alert_type": "wheelslip",
        "severity": "medium",
        "title": "Deslizamiento de Ruedas (ejemplo no reconocido)",
        "message": "Deslizamiento: 0.75 (umbral: 0.5)",
        "timestamp": "2025-12-03T00:40:27.388616",
        "data": {"wheelslip": 0.75, "threshold": 0.5, "slip_amount": 0.25},
        "acknowledged": False,
    },
]

with open(alerts_path, "w", encoding="utf-8") as f:
    json.dump(minimal, f, indent=2, ensure_ascii=False)

print("Wrote minimal alerts.json")
