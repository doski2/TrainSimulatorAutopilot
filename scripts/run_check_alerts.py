import os
import sys

try:
    # Prefer import at module top; if running as a script add repo root to sys.path
    from alert_system import check_alerts
except ImportError:
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from alert_system import check_alerts


if __name__ == '__main__':
    print(check_alerts())
