from tsc_integration import TSCIntegration
from web_dashboard import app


def test_metrics_endpoint_includes_tsc_io_and_uptime(monkeypatch):
    tsc = TSCIntegration()
    # Set deterministic metrics
    tsc.io_metrics = {
        "read_total_retries": 2,
        "read_last_latency_ms": 1.23,
        "read_attempts_last": 1,
        "write_total_retries": 3,
        "write_last_latency_ms": 2.34,
        "write_attempts_last": 2,
    }

    # Inject into web app
    monkeypatch.setattr('web_dashboard.tsc_integration', tsc)

    with app.test_client() as client:
        resp = client.get('/metrics')
        assert resp.status_code == 200
        text = resp.get_data(as_text=True)
        # Check presence of a couple of metrics
        assert 'tsc_io_read_total_retries' in text
        assert 'tsc_io_write_total_retries' in text
        assert 'dashboard_uptime_seconds' in text
        # Check numeric values appear
        assert 'tsc_io_read_total_retries 2.0' in text or 'tsc_io_read_total_retries 2' in text
        assert 'tsc_io_write_total_retries 3.0' in text or 'tsc_io_write_total_retries 3' in text
