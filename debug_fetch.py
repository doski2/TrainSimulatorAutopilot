import json

import requests

urls = ["http://localhost:5001/debug_data", "http://localhost:5000/debug_data"]
for u in urls:
    try:
        r = requests.get(u, timeout=2)
        print("URL", u, "Status", r.status_code)
        data = r.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        break
    except Exception as e:
        print("failed", u, e)
