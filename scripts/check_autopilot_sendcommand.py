import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from importlib import reload
from tempfile import TemporaryDirectory

import web_dashboard
from autopilot_system import AutopilotSystem
from tsc_integration import TSCIntegration

# Ensure fresh module state
reload(web_dashboard)

with TemporaryDirectory() as tmp:
    gd = os.path.join(tmp, 'GetData.txt')
    with open(gd, 'w', encoding='utf-8') as f:
        f.write('ControlName:CurrentSpeed\nControlValue:0.0\n')

    tsci = TSCIntegration(ruta_archivo=gd)
    sendfile = os.path.join(tmp, 'SendCommand.txt')
    tsci.ruta_archivo_comandos = sendfile

    # create plugin ack (simulate plugin online)
    ack_path = os.path.join(tmp, 'autopilot_state.txt')
    with open(ack_path, 'w', encoding='utf-8') as f:
        f.write('on')

    ap = AutopilotSystem()
    ap.tsc = tsci

    # Inject instances into dashboard
    web_dashboard.tsc_integration = tsci
    web_dashboard.autopilot_system = ap

    client = web_dashboard.app.test_client()
    resp = client.post('/api/control/start_autopilot')

    print('HTTP status:', resp.status_code)
    try:
        print('JSON:', resp.get_json())
    except Exception as exc:
        # Handle common expected non-JSON responses explicitly and log unexpected errors
        try:
            from werkzeug.exceptions import BadRequest as _BadRequest  # type: ignore
        except Exception:
            _BadRequest = None  # type: ignore

        # Flask/werkzeug may raise BadRequest on malformed JSON; json library may raise JSONDecodeError or ValueError
        try:
            import json as _json
        except Exception:
            _json = None  # pragma: no cover - defensive

        if _BadRequest is not None and isinstance(exc, _BadRequest):
            print('No JSON response: BadRequest (likely invalid JSON)')
        elif _json is not None and hasattr(_json, 'JSONDecodeError') and isinstance(exc, _json.JSONDecodeError):
            print(f'No JSON response: JSONDecodeError -> {exc}')
        elif isinstance(exc, ValueError):
            print(f'No JSON response: {exc}')
        else:
            # Unknown exception: print details and traceback to aid debugging
            import traceback

            print(f'Exception while getting JSON response: {exc}')
            traceback.print_exc()

    # Show sendfile and autopilot_commands.txt contents
    print('\nFiles produced:')
    print('SendCommand exists:', os.path.exists(sendfile), 'path:', sendfile)
    lua_file = os.path.join(tmp, 'autopilot_commands.txt')
    print('autopilot_commands exists:', os.path.exists(lua_file), 'path:', lua_file)

    if os.path.exists(sendfile):
        print('\n--- SendCommand.txt content ---')
        with open(sendfile, encoding='utf-8') as fh:
            print(fh.read())
    if os.path.exists(lua_file):
        print('\n--- autopilot_commands.txt content ---')
        with open(lua_file, encoding='utf-8') as fh:
            print(fh.read())

    # Also show plugin ack file content
    ack_file = os.path.join(tmp, 'autopilot_state.txt')
    print('\n--- autopilot_state.txt content ---')
    with open(ack_file, encoding='utf-8') as fh:
        print(fh.read())
