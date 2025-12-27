import os


def test_e2e_autopilot_writes_commands(tmp_path, monkeypatch):
    """E2E test: el autopilot lee GetData, toma una decisión y escribe comandos en disco.

    - Crea un GetData.txt temporal
    - Configura TSCIntegration para usar archivos temporales
    - Fuerza una decisión determinística en la IA
    - Llama a ejecutar_ciclo_control() y escribe comandos
    - Verifica que los archivos de comandos existen y contienen las líneas esperadas
    - Verifica que las métricas de I/O y IA se actualizaron
    """
    from autopilot_system import AutopilotSystem
    from tsc_integration import TSCIntegration

    # Preparar GetData.txt con datos simples
    getdata = tmp_path / "GetData.txt"
    getdata.write_text(
        "ControlName:CurrentSpeed\nControlValue:30.0\nControlName:CurrentSpeedLimit\nControlValue:20.0\n",
        encoding="utf-8",
    )

    # Configurar TSCIntegration para usar ruta temporal de datos y comandos
    tsci = TSCIntegration(ruta_archivo=str(getdata))
    sendfile = tmp_path / "SendCommand.txt"
    tsci.ruta_archivo_comandos = str(sendfile)
    tsci.write_lua_commands = True

    # Preparar Autopilot y conectar objetos
    ap = AutopilotSystem()
    ap.tsc = tsci
    ap.sesion_activa = True

    # Forzar IA a devolver una decisión conocida
    def fake_procesar(datos):
        return {"freno_tren": 0.8, "acelerador": 0.0}

    monkeypatch.setattr(ap.ia, "procesar_telemetria", fake_procesar)

    # Ejecutar ciclo de control (debería producir una decisión)
    resultado = ap.ejecutar_ciclo_control()
    assert resultado is not None

    # Enviar comandos (escritura atómica con reintentos)
    success = tsci.enviar_comandos({"freno_tren": 0.8, "acelerador": 0.0})
    assert success

    # Verificar que el archivo principal de comandos existe y contiene líneas
    assert os.path.exists(tsci.ruta_archivo_comandos)
    with open(tsci.ruta_archivo_comandos, encoding="utf-8") as fh:
        content = fh.read()
    assert ":" in content

    # Verificar archivo autopilot_commands.txt (Lua)
    lua_file = os.path.join(os.path.dirname(tsci.ruta_archivo_comandos), "autopilot_commands.txt")
    assert os.path.exists(lua_file)
    with open(lua_file, encoding="utf-8") as fh:
        lua_content = fh.read()
    assert ":" in lua_content

    # Verificar archivo legacy sendcommand.txt
    legacy_file = os.path.join(os.path.dirname(tsci.ruta_archivo_comandos), "sendcommand.txt")
    assert os.path.exists(legacy_file)
    with open(legacy_file, encoding="utf-8") as fh:
        legacy_content = fh.read()
    assert ":" in legacy_content

    # Métricas I/O y IA actualizadas
    io_metrics = tsci.get_io_metrics()
    assert io_metrics["write_attempts_last"] >= 1
    assert io_metrics["write_last_latency_ms"] >= 0.0
    assert ap.ia.metrics["decision_total"] >= 1
