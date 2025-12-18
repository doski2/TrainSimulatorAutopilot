"""Tests para control de monitor de rendimiento vía API"""

import os
import sys

# Añadir ruta del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from web_dashboard import app, performance_monitor


def test_toggle_performance_monitor():
    client = app.test_client()

    # Asegurarse de que inicialmente está detenido
    performance_monitor.stop_monitoring()
    assert not performance_monitor.is_monitoring

    # Iniciar via API
    resp = client.post("/api/control/toggle_performance")
    data = resp.get_json()
    assert data["success"] is True
    assert data["performance_monitoring"] is True
    assert performance_monitor.is_monitoring is True

    # Parar via API
    resp2 = client.post("/api/control/toggle_performance")
    data2 = resp2.get_json()
    assert data2["success"] is True
    assert data2["performance_monitoring"] is False
    assert performance_monitor.is_monitoring is False
