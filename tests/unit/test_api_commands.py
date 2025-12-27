import os
import sys
import tempfile

# Avoid importing heavy 3rd-party modules during unit tests by providing
# a minimal stub for bokeh if it's not installed in the test env.
import types

if 'bokeh' not in sys.modules:
    bokeh_stub = types.ModuleType('bokeh')
    bokeh_embed = types.ModuleType('bokeh.embed')
    bokeh_embed.server_document = lambda *args, **kwargs: ''  # type: ignore[attr-defined]
    sys.modules['bokeh'] = bokeh_stub
    sys.modules['bokeh.embed'] = bokeh_embed

import web_dashboard
from tools.poc_file_ack.consumer import Consumer


def test_api_commands_enqueue_no_wait():
    with tempfile.TemporaryDirectory() as d:
        # configure tsc_integration path to point to tmp dir
        if web_dashboard.tsc_integration is None:
            from tsc_integration import TSCIntegration

            web_dashboard.tsc_integration = TSCIntegration(ruta_archivo=None)
        web_dashboard.tsc_integration.ruta_archivo_comandos = os.path.join(d, 'SendCommand.txt')

        with web_dashboard.app.test_client() as client:
            resp = client.post('/api/commands', json={'type': 'set_regulator', 'value': 0.7, 'wait_for_ack': False})
            assert resp.status_code == 202
            data = resp.get_json()
            assert data['status'] == 'queued'
            assert 'id' in data
            # check that file exists
            cmd_file = os.path.join(d, f"cmd-{data['id']}.json")
            assert os.path.exists(cmd_file)


def test_api_commands_wait_for_ack():
    with tempfile.TemporaryDirectory() as d:
        # configure tsc_integration path to point to tmp dir
        if web_dashboard.tsc_integration is None:
            from tsc_integration import TSCIntegration

            web_dashboard.tsc_integration = TSCIntegration(ruta_archivo=None)
        web_dashboard.tsc_integration.ruta_archivo_comandos = os.path.join(d, 'SendCommand.txt')

        # start consumer
        c = Consumer(d, poll_interval=0.01, process_time=0.01)
        c.start()
        try:
            with web_dashboard.app.test_client() as client:
                # wait_for_ack parameter is now ignored; command is queued
                resp = client.post('/api/commands', json={'type': 'set_regulator', 'value': 0.8, 'wait_for_ack': True, 'timeout': 2.0, 'retries': 2})
                assert resp.status_code == 202
                data = resp.get_json()
                assert data['status'] == 'queued'
                assert 'id' in data
                # check that file exists
                cmd_file = os.path.join(d, f"cmd-{data['id']}.json")
                assert os.path.exists(cmd_file)
        finally:
            c.stop()
            c.join()
