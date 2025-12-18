import json
from pathlib import Path

p = Path(__file__).parent.parent / "alerts.json"
q = Path(__file__).parent.parent / "tests" / "fixtures" / "alerts_wheelslip_full.json"

with open(p, encoding="utf-8") as f:
    data = json.load(f)
print("alerts.json entries:", len(data))

with open(q, encoding="utf-8") as f:
    j = json.load(f)
print("fixtures type:", type(j))
if isinstance(j, dict):
    print("fixture keys:", list(j.keys()))
else:
    print("fixture length:", len(j))
