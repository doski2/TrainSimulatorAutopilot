import os
import sys
from importlib import reload
from tempfile import TemporaryDirectory

# Ensure project root is on sys.path before importing local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import web_dashboard
from autopilot_system import AutopilotSystem
from tsc_integration import TSCIntegration

# Reload in case module state changed during interactive debugging
reload(web_dashboard)

with TemporaryDirectory() as tmp:
    gd = os.path.join(tmp, 'GetData.txt')
    with open(gd, 'w', encoding='utf-8') as f:
        f.write('ControlName:CurrentSpeed\nControlValue:0.0\n')
    tsci = TSCIntegration(ruta_archivo=gd)
    sendfile = os.path.join(tmp, 'SendCommand.txt')
    tsci.ruta_archivo_comandos = sendfile
    autopilot_state_path = os.path.join(tmp, 'autopilot_state.txt')
    with open(autopilot_state_path, 'w', encoding='utf-8') as f:
        f.write('on')
    ap = AutopilotSystem()
    ap.tsc = tsci
    web_dashboard.tsc_integration = tsci
    web_dashboard.autopilot_system = ap
    client = web_dashboard.app.test_client()
    resp = client.post('/api/control/start_autopilot')
    print('STATUS', resp.status_code)
    print('JSON', resp.get_json())
