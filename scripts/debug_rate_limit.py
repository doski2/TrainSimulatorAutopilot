import os
import sys

sys.path.append(os.getcwd())

import web_dashboard as wd
from web_dashboard import app


class DummyTSC:
    def __init__(self):
        self.last = None

    def enviar_comandos(self, c):
        self.last = c
        return True


print(
    'limiter present?',
    getattr(wd, 'limiter', None) is not None,
    'limiter class:',
    type(getattr(wd, 'limiter', None)),
)
wd.tsc_integration = DummyTSC()
app.config['CONTROL_RATE_LIMIT'] = '1 per second'
client = app.test_client()
for i in range(1, 4):
    r = client.post('/api/control/set', json={'control': 'Regulator', 'value': 0.5})
    print(i, r.status_code)
    headers = getattr(r, 'headers', None)
    if headers is not None:
        print('headers:', headers)
    else:
        print('headers: <none>')

    try:
        j = r.get_json()
        print('json:', j)
    except Exception:
        print('json: <unavailable>')

