import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from alert_system import get_alert_system, check_alerts

print(check_alerts())
alert_sys = get_alert_system()
active = alert_sys.get_active_alerts()
print('Active alerts count:', len(active))
for a in active:
    print(a.to_dict())
