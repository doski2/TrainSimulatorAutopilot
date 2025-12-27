import os

from autopilot_system import AutopilotSystem
from tsc_integration import TSCIntegration
from web_dashboard import app, autopilot_metrics


def test_retry_autopilot_increments_metric_and_writes_command(tmp_path, monkeypatch):
    getdata = tmp_path / "GetData.txt"
    getdata.write_text("ControlName:CurrentSpeed\nControlValue:0.0\n", encoding="utf-8")

    tsci = TSCIntegration(ruta_archivo=str(getdata))
    sendfile = tmp_path / "SendCommand.txt"
    tsci.ruta_archivo_comandos = str(sendfile)

    ap = AutopilotSystem()
    ap.tsc = tsci

    monkeypatch.setattr('web_dashboard.tsc_integration', tsci)
    monkeypatch.setattr('web_dashboard.autopilot_system', ap)

    before = autopilot_metrics.get('retry_total', 0)

    with app.test_client() as client:
        resp = client.post('/api/control/retry_autopilot')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True

    after = autopilot_metrics.get('retry_total', 0)
    assert after == before + 1

    # check that command file contains start_autopilot
    assert os.path.exists(tsci.ruta_archivo_comandos)
    with open(tsci.ruta_archivo_comandos, encoding='utf-8') as fh:
        content = fh.read()
    assert 'start_autopilot' in content

