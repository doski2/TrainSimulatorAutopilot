import tempfile
from pathlib import Path

from autopilot_system import AutopilotSystem
from tsc_integration import TSCIntegration
from web_dashboard import app

p = Path(tempfile.mkdtemp())
getdata = p / 'GetData.txt'
getdata.write_text('ControlName:CurrentSpeed\nControlValue:0.0\n', encoding='utf-8')

# Configure TSCIntegration and autopilot
tsci = TSCIntegration(ruta_archivo=str(getdata))
sendfile = p / 'SendCommand.txt'
tsci.ruta_archivo_comandos = str(sendfile)
# create ack file
ack = p / 'autopilot_state.txt'
ack.write_text('on', encoding='utf-8')

ap = AutopilotSystem()
ap.tsc = tsci

import web_dashboard  # noqa: E402

web_dashboard.tsc_integration = tsci
web_dashboard.autopilot_system = ap

# Propagate exceptions so we can see them during debugging
app.testing = True
app.config['PROPAGATE_EXCEPTIONS'] = True

with app.test_client() as client:
    resp = client.post('/api/control/start_autopilot')
    print('status', resp.status_code)
    try:
        print('json', resp.get_json())
    except Exception as e:
        print('get_json failed', e)
    print('data', resp.get_data(as_text=True)[:2000])
