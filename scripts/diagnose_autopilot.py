import os
import sys
from typing import cast

# Ensure project root is on sys.path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask.testing import FlaskClient

from web_dashboard import app, tsc_integration

print('TSCIntegration object:', bool(tsc_integration))
if tsc_integration:
    print('ruta_archivo_comandos:', tsc_integration.ruta_archivo_comandos)
    plugins_dir = os.path.dirname(tsc_integration.ruta_archivo_comandos)
    files = ['autopilot_commands.txt','SendCommand.txt','sendcommand.txt','autopilot_state.txt','autopilot_plugin_loaded.txt']
    for f in files:
        p = os.path.join(plugins_dir, f)
        print(f, 'exists=', os.path.exists(p), 'mtime=', os.path.getmtime(p) if os.path.exists(p) else None)
        if os.path.exists(p):
            print('--- content of', f, '---')
            try:
                print(open(p, encoding='utf-8', errors='replace').read())
            except Exception as e:
                print('read error', e)
            print('--- end ---')

# Annotate the test client to satisfy static type checkers (Pylance)

c = cast(FlaskClient, app.test_client())
with c:
    r = c.get('/api/status')
    print('/api/status ->', r.status_code, r.get_json())

# Check permissions of plugin dir
if tsc_integration:
    plugins_dir = os.path.dirname(tsc_integration.ruta_archivo_comandos)
    try:
        print('Plugin dir:', plugins_dir)
        stat = os.stat(plugins_dir)
        print('Plugin dir owner uid/gid:', getattr(stat, 'st_uid', None), getattr(stat, 'st_gid', None))
    except Exception as e:
        print('Could not stat plugin dir:', e)
