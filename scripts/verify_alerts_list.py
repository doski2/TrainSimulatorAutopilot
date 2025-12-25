import os
import sys

try:
    # Prefer import at module top; add repo root to sys.path when running as script
    from alert_system import check_alerts, get_alert_system
except ImportError:
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from alert_system import check_alerts, get_alert_system


if __name__ == '__main__':
    print(check_alerts())
    alert_sys = get_alert_system()
    active = alert_sys.get_active_alerts()
    print('Active alerts count:', len(active))
    for a in active:
        print(a.to_dict())
