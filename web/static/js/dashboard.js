// Dashboard JavaScript for Train Simulator Autopilot
let socket;
// Conjunto de alert IDs que ya fueron notificadas en el cliente
let knownAlertIds = new Set();
let speedChart;
let telemetryHistory = [];
let maxHistoryPoints = 50;

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

function initializeDashboard() {
    // Inicializar gráfico de velocidad
    initializeCharts();

    // Conectar WebSocket
    connectWebSocket();

    // Configurar event listeners
    setupEventListeners();

    // Inicializar configuración
    initializeSettings();

    // Solicitar datos iniciales
    setTimeout(() => {
        if (socket && socket.connected) {
            socket.emit('request_telemetry');
        }
    }, 1000);

    // Verificar que los elementos críticos existen
    const criticalElements = [
        'settings-link',
        'settings-panel',
        'theme-select',
        'animations-toggle'
        , 'autobrake-by-signal'
    ];

    criticalElements.forEach(id => {
        const element = document.getElementById(id);
    });
}

function initializeCharts() {
    const ctx = document.getElementById('speedChart').getContext('2d');

    speedChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Velocidad (km/h)',
                data: [],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }, {
                label: 'Límite de Velocidad',
                data: [],
                borderColor: '#dc3545',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                borderWidth: 2,
                borderDash: [5, 5],
                fill: false,
                tension: 0.4
            }, {
                label: 'Velocidad Predicha',
                data: [],
                borderColor: '#ffc107',
                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                borderWidth: 2,
                borderDash: [10, 5],
                fill: false,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 0 // Deshabilitar animaciones para mejor rendimiento
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#ffffff'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff'
                    }
                }
            }
        }
    });
}

function connectWebSocket() {
    socket = io();

    socket.on('connect', function() {
        updateConnectionStatus(true);
        showAlert('Conectado al servidor', 'success');
    });

    socket.on('disconnect', function() {
        updateConnectionStatus(false);
        showAlert('Desconectado del servidor', 'danger');
    });

    socket.on('telemetry_update', function(data) {
        try {
            updateTelemetry(data);
        } catch (error) {
            console.error('❌ Error en updateTelemetry:', error);
            console.error('❌ Datos recibidos:', data);
        }
    });

    socket.on('system_message', function(data) {
        showAlert(data.message, data.type);
    });

    socket.on('autobrake_status', function(data) {
        try {
            const enabled = data.autobrake_by_signal;
            dashboardConfig.autobrakeBySignal = enabled;
            const el = document.getElementById('autobrake-by-signal');
            if (el) el.checked = enabled;
            showAlert('Autobrake por señal actualizado: ' + enabled, 'info');
        } catch (e) {
            console.warn('Error handling autobrake_status event', e);
        }
    });

    socket.on('connect_error', function(error) {
        console.error('Error de conexión WebSocket:', error);
        showAlert('Error de conexión con el servidor', 'danger');
    });
}

function setupEventListeners() {
    // Controles de piloto automático
    document.getElementById('start-autopilot').addEventListener('click', () => {
        controlAction('start_autopilot');
    });

    document.getElementById('stop-autopilot').addEventListener('click', () => {
        controlAction('stop_autopilot');
    });

    // Controles predictivos
    document.getElementById('start-predictive').addEventListener('click', () => {
        controlAction('start_predictive');
    });

    document.getElementById('stop-predictive').addEventListener('click', () => {
        controlAction('stop_predictive');
    });

    document.getElementById('train-model').addEventListener('click', () => {
        controlAction('train_model');
    });

    // Controles de locomotora
    document.getElementById('toggle-doors').addEventListener('click', () => {
        controlAction('toggle_doors');
    });

    document.getElementById('toggle-lights').addEventListener('click', () => {
        controlAction('toggle_lights');
    });

    document.getElementById('emergency-brake').addEventListener('click', () => {
        controlAction('emergency_brake');
    });

    // Controles de reportes
    document.getElementById('generate-report').addEventListener('click', () => {
        generateReport();
    });

    document.getElementById('view-reports').addEventListener('click', () => {
        viewReports();
    });

    // Control de visualizaciones Bokeh
    document.getElementById('load-bokeh').addEventListener('click', () => {
        loadBokehVisualizations();
    });
}

function controlAction(action) {
    fetch(`/api/control/${action}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Action executed successfully
        } else {
            showAlert(`Error en acción ${action}: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        console.error('Error en control:', error);
        showAlert('Error de comunicación con el servidor', 'danger');
    });
}

function updateTelemetry(data) {
    const telemetry = data.telemetry || {};
    console.debug('[UI] telemetry_update received', telemetry); // Debug log for telemetry updates
    console.debug('[UI] active_alerts payload', activeAlerts); // Debug check for active alerts payload

    // Utility: safely set textContent if element exists
    function safeSetText(elementId, text) {
        const el = document.getElementById(elementId);
        if (el) {
            el.textContent = text;
        }
    }
    const predictions = data.predictions || {};
    const multiLoco = data.multi_loco || {};
    const systemStatus = data.system_status || {};
    const activeAlerts = data.active_alerts || [];
    const performance = data.performance || {};
    const reports = data.reports || {};

    // Actualizar alertas activas
    updateActiveAlerts(activeAlerts);

    // Actualizar métricas de rendimiento
    updatePerformanceMetrics(performance);

    // Actualizar estado de reportes
    updateReportsStatus(reports);

    // Mostrar mensaje simple para confirmar que funciona
    const speedValue = telemetry.velocidad_actual;
    const speedElement = document.getElementById('speed-value');

    const unitPref = (dashboardConfig && dashboardConfig.speedUnit) ? dashboardConfig.speedUnit : 'kmh';
    // El backend entrega km/h (según integración). Si el usuario quiere mph o m/s, convertir.
    function formatSpeedForDisplay(kmhValue, unit) {
      if (!Number.isFinite(kmhValue)) return null;
      if (unit === 'mph') {
        const mph = kmhValue / 1.609344;
        return `${mph.toFixed(1)} mph`;
      } else if (unit === 'ms') {
        const ms = kmhValue / 3.6;
        return `${ms.toFixed(1)} m/s`;
      }
      // default kmh
      return `${kmhValue.toFixed(1)} km/h`;
    }

    if (speedElement) {
      const display = formatSpeedForDisplay(speedValue, unitPref);
      if (display !== null) {
        speedElement.textContent = display;
      } else {
        speedElement.textContent = '--';
      }
    }
    
    // Mostrar aceleración combinada (positiva = acelerando, negativa = frenando)
    const acceleration = telemetry.aceleracion || 0;
    const accelText = acceleration >= 0 ? 
        `+${acceleration.toFixed(3)}` : 
        acceleration.toFixed(3);
    safeSetText('acceleration-value', accelText + ' m/s²');
    
    // Mostrar pendiente con descripción intuitiva
    updateGradientDisplay(telemetry.pendiente);
    
    // Mostrar esfuerzo de tracción en N
    const tractiveEffort = telemetry.esfuerzo_traccion;
    if (tractiveEffort !== undefined && tractiveEffort !== null) {
        // Mostrar directamente en N
        safeSetText('tractive-effort-value', tractiveEffort.toFixed(0) + ' N');
    } else {
        safeSetText('tractive-effort-value', '--');
    }
    
    // Mostrar RPM del motor
    const rpm = telemetry.rpm;
    if (rpm !== undefined && rpm !== null) {
        safeSetText('rpm-value', rpm.toFixed(0) + ' RPM');
    } else {
        safeSetText('rpm-value', '--');
    }
    
    // Mostrar amperaje
    const amperaje = telemetry.amperaje;
    if (amperaje !== undefined && amperaje !== null) {
        safeSetText('amperage-value', amperaje.toFixed(1) + ' A');
    } else {
        safeSetText('amperage-value', '--');
    }
    
    // Mostrar deslizamiento de ruedas (usar valor normalizado si está disponible), y mostrar raw
    const deslizamiento = telemetry.deslizamiento_ruedas_intensidad !== undefined ? telemetry.deslizamiento_ruedas_intensidad : telemetry.deslizamiento_ruedas;
    const deslizamiento_raw = telemetry.deslizamiento_ruedas_raw !== undefined ? telemetry.deslizamiento_ruedas_raw : telemetry.deslizamiento_ruedas;
    if (deslizamiento !== undefined && deslizamiento !== null) {
        // Mostrar intensidad 0..1 con dos decimales
        safeSetText('wheelslip-value', deslizamiento.toFixed(2));
        // Mostrar valor raw si existe
        if (deslizamiento_raw !== undefined && deslizamiento_raw !== null) {
            safeSetText('wheelslip-raw-value', deslizamiento_raw.toFixed(1));
        }
        // Estado visual: considerar patinaje si raw > 1.05 o intensity > 0.5
        const statusEl = document.getElementById('wheelslip-status');
        const slipFlag = (deslizamiento_raw > 1.05) || (deslizamiento > 0.5);
        if (statusEl) {
            statusEl.className = slipFlag ? 'badge bg-warning ms-2' : 'badge bg-success ms-2';
            statusEl.textContent = slipFlag ? 'PATINA' : 'OK';
        }
    } else {
        safeSetText('wheelslip-value', '--');
    }
    
    // Mostrar presiones de frenos
    const brakePipePressure = telemetry.presion_tubo_freno;
    const brakePipePresent = telemetry.presion_tubo_freno_presente || telemetry.presion_tubo_freno_mostrada_presente;
    if (brakePipePresent && brakePipePressure !== undefined && brakePipePressure !== null) {
        let valText = brakePipePressure.toFixed(0) + ' PSI';
        if (telemetry.presion_tubo_freno_inferida) valText += ' (inf)';
        safeSetText('brake-pipe-value', valText);
    } else {
        safeSetText('brake-pipe-value', '--');
    }
    
    const locoBrakePressure = telemetry.presion_freno_loco;
    const locoBrakePresent = telemetry.presion_freno_loco_presente || telemetry.presion_freno_loco_mostrada_presente;
    if (locoBrakePresent && locoBrakePressure !== undefined && locoBrakePressure !== null) {
        let valText = locoBrakePressure.toFixed(0) + ' PSI';
        if (telemetry.presion_freno_loco_inferida) valText += ' (inf)';
        safeSetText('loco-brake-value', valText);
    } else {
        safeSetText('loco-brake-value', '--');
    }
    
    const trainBrakePressure = telemetry.presion_freno_tren;
    const trainBrakePresent = telemetry.presion_freno_tren_presente;
    if (trainBrakePresent && trainBrakePressure !== undefined && trainBrakePressure !== null) {
        safeSetText('train-brake-value', trainBrakePressure.toFixed(0) + ' PSI');
    } else {
        safeSetText('train-brake-value', '--');
    }

    // Posición del control de freno de tren (0..1 -> %)
    const trainBrakePos = telemetry.posicion_freno_tren;
    const trainBrakePosPresent = telemetry.posicion_freno_tren_presente;
    const frenoTrenEstimate = telemetry.freno_tren;
    if (trainBrakePosPresent && trainBrakePos !== undefined && trainBrakePos !== null) {
        safeSetText('train-brake-pos-value', Math.round(trainBrakePos * 100) + '%');
    } else if (frenoTrenEstimate !== undefined && frenoTrenEstimate !== null) {
        let suffix = '';
        if (telemetry.presion_freno_tren_inferida) suffix = ' (inf)';
        safeSetText('train-brake-pos-value', Math.round(frenoTrenEstimate * 100) + '%' + suffix);
    } else {
        safeSetText('train-brake-pos-value', '--');
    }
    
    const brakePipeTailPressure = telemetry.presion_tubo_freno_cola;
    const brakePipeTailPresent = telemetry.presion_tubo_freno_cola_presente || (telemetry.presion_tubo_freno_cola !== undefined && telemetry.presion_tubo_freno_cola !== null);
    if (brakePipeTailPresent) {
        safeSetText('brake-pipe-tail-value', brakePipeTailPressure.toFixed(0) + ' PSI');
    } else {
        safeSetText('brake-pipe-tail-value', '--');
    }

    // Badge de presencia / inferencia para Tubería de Freno Cola
    const tailBadge = document.getElementById('brake-pipe-tail-presence');
    if (tailBadge) {
        if (telemetry.presion_tubo_freno_cola_presente) {
            tailBadge.textContent = 'PRESENTE';
            tailBadge.className = 'badge bg-success ms-2';
        } else if (telemetry.presion_tubo_freno_cola !== undefined && telemetry.presion_tubo_freno_cola !== null) {
            tailBadge.textContent = 'INFERIDO';
            tailBadge.className = 'badge bg-warning text-dark ms-2';
        } else {
            tailBadge.textContent = 'NO';
            tailBadge.className = 'badge bg-secondary ms-2';
        }
    }
    
    const locoBrakeDisplayedPressure = telemetry.presion_freno_loco_mostrada;
    const locoBrakeDisplayedPresent = telemetry.presion_freno_loco_mostrada_presente;
    if (locoBrakeDisplayedPresent && locoBrakeDisplayedPressure !== undefined && locoBrakeDisplayedPressure !== null) {
        safeSetText('loco-brake-displayed-value', locoBrakeDisplayedPressure.toFixed(0) + ' PSI');
    } else {
        safeSetText('loco-brake-displayed-value', '--');
    }
    
    const eqReservoirPressure = telemetry.presion_deposito_equalizacion;
    const eqReservoirPresent = telemetry.eq_reservoir_presente;
    if (eqReservoirPresent && eqReservoirPressure !== undefined && eqReservoirPressure !== null) {
        safeSetText('eq-reservoir-value', eqReservoirPressure.toFixed(0) + ' PSI');
    } else {
        safeSetText('eq-reservoir-value', '--');
    }
    
    const mainReservoirPressure = telemetry.presion_deposito_principal;
    const mainReservoirPresent = telemetry.presion_deposito_principal_presente;
    if (mainReservoirPresent && mainReservoirPressure !== undefined && mainReservoirPressure !== null) {
        safeSetText('main-reservoir-value', mainReservoirPressure.toFixed(0) + ' PSI');
    } else {
        safeSetText('main-reservoir-value', '--');
    }
    
    const auxReservoirPressure = telemetry.presion_deposito_auxiliar;
    if (auxReservoirPressure !== undefined && auxReservoirPressure !== null) {
        safeSetText('aux-reservoir-value', auxReservoirPressure.toFixed(0) + ' PSI');
    } else {
        safeSetText('aux-reservoir-value', '--');
    }
    
    // Mostrar combustible
    const fuelLevel = telemetry.combustible;
    const fuelPct = telemetry.combustible_porcentaje;
    const fuelGal = telemetry.combustible_galones;
    if (fuelGal !== undefined && fuelGal !== null) {
        safeSetText('fuel-level-value', (fuelGal).toFixed(1) + ' gal');
    } else if (fuelPct !== undefined && fuelPct !== null) {
        safeSetText('fuel-level-value', (fuelPct).toFixed(1) + '%');
    } else if (fuelLevel !== undefined && fuelLevel !== null) {
        // Legacy fallback: assume fraction 0..1
        safeSetText('fuel-level-value', (fuelLevel * 100).toFixed(1) + '%');
    } else {
        safeSetText('fuel-level-value', '--');
    }
    
    // Mostrar distancia recorrida
    const distanceTravelled = telemetry.distancia_recorrida;
    if (distanceTravelled !== undefined && distanceTravelled !== null) {
        safeSetText('distance-travelled-value', (distanceTravelled / 1000).toFixed(2) + ' km');
    } else {
        safeSetText('distance-travelled-value', '--');
    }
    
    // Mostrar límite de velocidad actual
    const currentSpeedLimit = telemetry.limite_velocidad;
    if (currentSpeedLimit !== undefined && currentSpeedLimit !== null) {
        safeSetText('speed-limit', currentSpeedLimit.toFixed(0) + ' km/h');
    } else {
        safeSetText('speed-limit', '--');
    }
    
    // Mostrar límite de velocidad siguiente
    const nextSpeedLimit = telemetry.limite_velocidad_siguiente;
    if (nextSpeedLimit !== undefined && nextSpeedLimit !== null) {
        safeSetText('next-speed-limit-value', nextSpeedLimit.toFixed(0) + ' km/h');
    } else {
        safeSetText('next-speed-limit-value', '--');
    }
    
    // Mostrar distancia al límite siguiente
    const nextSpeedDistance = telemetry.distancia_limite_siguiente;
    if (nextSpeedDistance !== undefined && nextSpeedDistance !== null) {
        safeSetText('next-speed-distance-value', nextSpeedDistance.toFixed(0) + ' m');
    } else {
        safeSetText('next-speed-distance-value', '--');
    }
    
    // Mostrar tiempo de simulación
    const simulationTime = telemetry.tiempo_simulacion;
    if (simulationTime !== undefined && simulationTime !== null) {
        const minutes = Math.floor(simulationTime / 60);
        const seconds = Math.floor(simulationTime % 60);
        safeSetText('simulation-time-value', `${minutes}:${seconds.toString().padStart(2, '0')}`);
    } else {
        safeSetText('simulation-time-value', '--');
    }
    
    // Mostrar señal principal (usar `senal_procesada` cuando esté disponible)
    const signalAspect = telemetry.senal_procesada !== undefined && telemetry.senal_procesada !== null ? telemetry.senal_procesada : telemetry.senal_principal;
    if (signalAspect !== undefined && signalAspect !== null) {
        const signalText = signalAspect === 0 ? 'ROJA' : signalAspect === 1 ? 'AMARILLA' : signalAspect === 2 ? 'VERDE' : 'DESCONOCIDA';
        const signalClass = signalAspect === 0 ? 'text-danger' : signalAspect === 1 ? 'text-warning' : signalAspect === 2 ? 'text-success' : 'text-muted';
        document.getElementById('main-signal').innerHTML = `<span class="${signalClass}">${signalText}</span>`;
    } else {
        safeSetText('main-signal', '--');
    }
    // Mostrar señal avanzada (distant) si existe
    const distantAspect = telemetry.senal_avanzada;
    if (distantAspect !== undefined && distantAspect !== null) {
        const distantText = distantAspect === 0 ? 'ROJA' : distantAspect === 1 ? 'AMARILLA' : distantAspect === 2 ? 'VERDE' : 'DESCONOCIDA';
        const distantClass = distantAspect === 0 ? 'text-danger' : distantAspect === 1 ? 'text-warning' : distantAspect === 2 ? 'text-success' : 'text-muted';
        const dsEl = document.getElementById('distant-signal');
        if (dsEl) dsEl.innerHTML = `<span class="${distantClass}">${distantText}</span>`;
    } else {
        safeSetText('distant-signal', '--');
    }

    // Set last update timestamp to help debugging
    try {
        safeSetText('last-update', new Date().toLocaleTimeString());
    } catch (e) {}
}

function updateMetric(elementId, value, decimals = 0) {
    const element = document.getElementById(elementId);
    if (element && value !== undefined && value !== null) {
        element.textContent = typeof value === 'number' ? value.toFixed(decimals) : value;
    } else if (element) {
        element.textContent = '--';
    }
}

function updateSystemStatus(status) {
    // Estado del piloto automático
    const autopilotBadge = document.getElementById('autopilot-status');
    const startBtn = document.getElementById('start-autopilot');
    const stopBtn = document.getElementById('stop-autopilot');

    if (status.autopilot_active) {
        autopilotBadge.className = 'badge bg-success';
        autopilotBadge.textContent = 'ACTIVO';
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        autopilotBadge.className = 'badge bg-danger';
        autopilotBadge.textContent = 'INACTIVO';
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }

    // Estado predictivo
    const predictiveBadge = document.getElementById('predictive-status');
    const startPredBtn = document.getElementById('start-predictive');
    const stopPredBtn = document.getElementById('stop-predictive');

    if (status.predictive_active) {
        predictiveBadge.className = 'badge bg-success';
        predictiveBadge.textContent = 'ACTIVO';
        startPredBtn.disabled = true;
        stopPredBtn.disabled = false;
    } else {
        predictiveBadge.className = 'badge bg-danger';
        predictiveBadge.textContent = 'INACTIVO';
        startPredBtn.disabled = false;
        stopPredBtn.disabled = true;
    }

    // Otros estados
    updateStatusBadge('tsc-connected', status.tsc_connected);
    updateStatusBadge('multi-loco-status', status.multi_loco_active);
    updateStatusBadge('model-trained', status.predictive_active);
    updateStatusBadge('brake-pressure-status', status.brake_pressure_present);

    // Contador de actualizaciones
    safeSetText('update-count', status.telemetry_updates || 0);
}

function updateStatusBadge(elementId, isActive) {
    const element = document.getElementById(elementId);
    if (element) {
        element.className = `badge ${isActive ? 'bg-success' : 'bg-danger'}`;
        element.textContent = isActive ? 'SÍ' : 'NO';
    }
}

function updateChart(telemetry, predictions) {
    if (!speedChart) return;

    // Agregar nuevo punto
    const timestamp = new Date().toLocaleTimeString();

    telemetryHistory.push({
        time: timestamp,
        speed: telemetry.velocidad_actual || 0,  // Siempre almacenar en km/h
        limit: telemetry.limite_velocidad || 160,  // Siempre almacenar en km/h
        predicted: predictions.velocidad_actual || null  // Siempre almacenar en km/h
    });

    // Mantener máximo de puntos
    if (telemetryHistory.length > maxHistoryPoints) {
        telemetryHistory.shift();
    }

    // Actualizar gráfico (convertir a la unidad actual para mostrar)
    function convertSpeed(kmhValue) {
        if (dashboardConfig.speedUnit === 'mph') {
            return kmhValue / 1.609344;
        } else if (dashboardConfig.speedUnit === 'ms') {
            return kmhValue / 3.6;
        }
        return kmhValue; // kmh
    }

    speedChart.data.labels = telemetryHistory.map(point => point.time);
    speedChart.data.datasets[0].data = telemetryHistory.map(point => convertSpeed(point.speed));
    speedChart.data.datasets[1].data = telemetryHistory.map(point => convertSpeed(point.limit));
    speedChart.data.datasets[2].data = telemetryHistory.map(point => point.predicted !== null ? convertSpeed(point.predicted) : null);

    speedChart.update('none'); // Sin animación para mejor rendimiento
}

function updatePredictions(predictions) {
    const container = document.getElementById('predictions-content');

    if (!predictions || Object.keys(predictions).length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                <p>Esperando predicciones...</p>
            </div>
        `;
        return;
    }

    const predictionItems = [
        { label: 'Velocidad', value: predictions.velocidad_actual, unit: dashboardConfig.speedUnit === 'kmh' ? 'km/h' : (dashboardConfig.speedUnit === 'mph' ? 'mph' : 'm/s'), decimals: 1 },
        { label: 'Acelerador', value: predictions.acelerador, unit: '%', decimals: 1, multiplier: 100 },
        { label: 'Freno', value: predictions.freno_tren, unit: '%', decimals: 1, multiplier: 100 },
        { label: 'Pendiente', value: predictions.pendiente, unit: '‰', decimals: 1 },
        { label: 'Límite Vel.', value: predictions.limite_velocidad, unit: dashboardConfig.speedUnit === 'kmh' ? 'km/h' : (dashboardConfig.speedUnit === 'mph' ? 'mph' : 'm/s'), decimals: 0 }
    ];

    let html = '<div class="prediction-list">';
    predictionItems.forEach(item => {
        if (item.value !== undefined && item.value !== null) {
            let displayValue = item.value;
            if (item.multiplier) displayValue *= item.multiplier;
            displayValue = displayValue.toFixed(item.decimals);

            html += `
                <div class="prediction-item">
                    <span class="prediction-label">${item.label}:</span>
                    <span class="prediction-value">${displayValue} ${item.unit}</span>
                </div>
            `;
        }
    });
    html += '</div>';

    container.innerHTML = html;
}

function updateLocomotives(multiLoco) {
    const container = document.getElementById('locomotives-content');

    if (!multiLoco || Object.keys(multiLoco).length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-search fa-2x mb-3"></i>
                <p>No se detectaron locomotoras activas</p>
            </div>
        `;
        return;
    }

    let html = '<div class="row">';

    Object.entries(multiLoco).forEach(([locoId, data]) => {
        const speed = data.velocidad_actual || 0;
        const throttle = data.acelerador ? (data.acelerador * 100) : 0;
        const brake = data.freno_tren ? (data.freno_tren * 100) : 0;
        const limit = data.limite_velocidad || 160;

        // Convertir velocidad y límite según unidad configurada
        const speedUnit = dashboardConfig.speedUnit === 'kmh' ? 'km/h' : (dashboardConfig.speedUnit === 'mph' ? 'mph' : 'm/s');
        const displaySpeed = dashboardConfig.speedUnit === 'mph' ? (speed / 1.609344).toFixed(1) : speed.toFixed(1);
        const displayLimit = dashboardConfig.speedUnit === 'mph' ? (limit / 1.609344).toFixed(0) : limit.toFixed(0);

        html += `
            <div class="col-md-6 mb-3">
                <div class="locomotive-card ${speed > 0 ? 'active' : ''}">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="mb-0">
                            <i class="fas fa-train me-2"></i>
                            ${locoId}
                        </h6>
                        <span class="badge ${speed > 0 ? 'bg-success' : 'bg-secondary'}">
                            ${speed > 0 ? 'Activa' : 'Inactiva'}
                        </span>
                    </div>
                    <div class="row text-center">
                        <div class="col-6">
                            <div class="h4 mb-0">${displaySpeed}</div>
                            <small>Velocidad (${speedUnit})</small>
                        </div>
                        <div class="col-6">
                            <div class="h4 mb-0">${displayLimit}</div>
                            <small>Límite (${speedUnit})</small>
                        </div>
                    </div>
                    <div class="row text-center mt-2">
                        <div class="col-6">
                            <div class="small">${throttle.toFixed(1)}% Acel</div>
                        </div>
                        <div class="col-6">
                            <div class="small">${brake.toFixed(1)}% Freno</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        statusElement.className = `badge ${connected ? 'bg-success' : 'bg-danger'}`;
        statusElement.innerHTML = `<i class="fas fa-circle"></i> ${connected ? 'Conectado' : 'Desconectado'}`;
    }
}

function showAlert(message, type = 'info', sticky = false) {
    const alertContainer = document.getElementById('alert-container');

    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-info-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    alertContainer.insertAdjacentHTML('beforeend', alertHtml);

    // Auto-remover después de 5 segundos a menos que sea persistente (sticky)
    if (!sticky) {
        setTimeout(() => {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                alertElement.remove();
            }
        }, 5000);
    }
}

// Funciones de utilidad
function formatNumber(num, decimals = 1) {
    if (num === null || num === undefined) return '--';
    return Number(num).toFixed(decimals);
}

function updateGradientDisplay(gradientValue) {
    const gradientElement = document.getElementById('gradient-value');
    const gradientLabel = document.getElementById('gradient-label');

    if (gradientValue !== undefined && gradientValue !== null) {
        const value = Math.abs(gradientValue).toFixed(1);
        const absValue = Math.abs(gradientValue);

        // Determinar dirección y descripción
        let direction = '';
        let description = '';

        if (gradientValue > 0) {
            direction = '↘️';
            description = 'Bajada';
        } else if (gradientValue < 0) {
            direction = '↗️';
            description = 'Subida';
        } else {
            direction = '➡️';
            description = 'Plano';
        }

        // Determinar intensidad
        let intensity = '';
        if (absValue < 1) {
            intensity = 'Muy suave';
        } else if (absValue < 5) {
            intensity = 'Suave';
        } else if (absValue < 15) {
            intensity = 'Moderada';
        } else if (absValue < 30) {
            intensity = 'Fuerte';
        } else {
            intensity = 'Muy fuerte';
        }

        // Actualizar display
        gradientElement.textContent = `${direction} ${value}`;
        gradientLabel.textContent = `${description} ${intensity} (${value} ‰)`;
    } else {
        gradientElement.textContent = '--';
        gradientLabel.textContent = 'Pendiente (‰)';
    }
}

// ==================== FUNCIONALIDAD DE CONFIGURACIÓN ====================

// Variables de configuración
let dashboardConfig = {
    theme: 'dark',
    animations: true,
    updateInterval: 1000,
    historyPoints: 50,
    speedUnit: 'kmh',
    alerts: {
        speedLimit: true,
        emergency: true,
        system: true
    }
    ,autobrakeBySignal: true
};

// Inicializar configuración
function initializeSettings() {
    loadSettings();
    setupSettingsEventListeners();
    applyTheme();
    updateSpeedUnit();
    // Consultar estado en servidor para sincronizar autobrake si no está en localStorage
    fetch('/api/autobrake/status')
        .then(r => r.json())
        .then(d => {
            if (d && typeof d.autobrake_by_signal !== 'undefined') {
                dashboardConfig.autobrakeBySignal = d.autobrake_by_signal;
                const el = document.getElementById('autobrake-by-signal');
                if (el) el.checked = d.autobrake_by_signal;
                localStorage.setItem('trainSimulatorDashboardConfig', JSON.stringify(dashboardConfig));
            }
        })
        .catch(() => {});
}

// Configurar event listeners para configuración
function setupSettingsEventListeners() {
    // Toggle del panel de configuración
    const settingsLink = document.getElementById('settings-link');

    if (settingsLink) {
        settingsLink.addEventListener('click', function(e) {
            e.preventDefault();
            showSettingsModal();
        });
    } else {
        console.error('❌ Settings link element not found!');
    }

    // Guardar configuración
    const saveBtn = document.getElementById('save-settings');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveSettings);
    }

    // Restaurar configuración
    const resetBtn = document.getElementById('reset-settings');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetSettings);
    }

    // Cambios en tiempo real
    const themeSelect = document.getElementById('theme-select');
    if (themeSelect) {
        themeSelect.addEventListener('change', function() {
            dashboardConfig.theme = this.value;
            applyTheme();
            localStorage.setItem('trainSimulatorDashboardConfig', JSON.stringify(dashboardConfig));
        });
    }

    const animationsToggle = document.getElementById('animations-toggle');
    if (animationsToggle) {
        animationsToggle.addEventListener('change', function() {
            dashboardConfig.animations = this.checked;
            applyAnimations();
            localStorage.setItem('trainSimulatorDashboardConfig', JSON.stringify(dashboardConfig));
        });
    }

    const updateInterval = document.getElementById('update-interval');
    if (updateInterval) {
        updateInterval.addEventListener('change', function() {
            dashboardConfig.updateInterval = parseInt(this.value);
            updateRefreshRate();
            localStorage.setItem('trainSimulatorDashboardConfig', JSON.stringify(dashboardConfig));
        });
    }

    const historyPoints = document.getElementById('history-points');
    if (historyPoints) {
        historyPoints.addEventListener('change', function() {
            dashboardConfig.historyPoints = parseInt(this.value);
            maxHistoryPoints = dashboardConfig.historyPoints;
            localStorage.setItem('trainSimulatorDashboardConfig', JSON.stringify(dashboardConfig));
        });
    }

    const speedUnit = document.getElementById('speed-unit');
    if (speedUnit) {
        speedUnit.addEventListener('change', function() {
            dashboardConfig.speedUnit = this.value;
            updateSpeedUnit();
            localStorage.setItem('trainSimulatorDashboardConfig', JSON.stringify(dashboardConfig));
        });
    }

    // Alertas
    const alertSpeedLimit = document.getElementById('alert-speed-limit');
    if (alertSpeedLimit) {
        alertSpeedLimit.addEventListener('change', function() {
            dashboardConfig.alerts.speedLimit = this.checked;
            localStorage.setItem('trainSimulatorDashboardConfig', JSON.stringify(dashboardConfig));
        });
    }

    const alertEmergency = document.getElementById('alert-emergency');
    if (alertEmergency) {
        alertEmergency.addEventListener('change', function() {
            dashboardConfig.alerts.emergency = this.checked;
            localStorage.setItem('trainSimulatorDashboardConfig', JSON.stringify(dashboardConfig));
        });
    }

    const alertSystem = document.getElementById('alert-system');
    if (alertSystem) {
        alertSystem.addEventListener('change', function() {
            dashboardConfig.alerts.system = this.checked;
            localStorage.setItem('trainSimulatorDashboardConfig', JSON.stringify(dashboardConfig));
        });
    }

    const autobrakeCheckbox = document.getElementById('autobrake-by-signal');
    if (autobrakeCheckbox) {
        autobrakeCheckbox.addEventListener('change', function() {
            dashboardConfig.autobrakeBySignal = this.checked;
            // Persist to server
            // Emit socket event for instant toggling and persistence
            try {
                if (socket && socket.connected) {
                    socket.emit('toggle_autobrake_by_signal', { enabled: this.checked });
                }
            } catch (e) {}

            fetch('/api/autobrake', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ enabled: this.checked })
            }).then(r => r.json()).then(d => {
                if (!d.success) {
                    showAlert('Error guardando autobrake: ' + (d.error || 'unknown'), 'danger');
                }
            }).catch(e => {
                showAlert('Error guardando autobrake en servidor', 'danger');
            });
            localStorage.setItem('trainSimulatorDashboardConfig', JSON.stringify(dashboardConfig));
        });
    }
}

// Mostrar/ocultar panel de configuración
function showSettingsModal() {
    // Cargar configuración en la UI
    loadSettingsToUI();

    // Mostrar modal usando Bootstrap
    const modal = new bootstrap.Modal(document.getElementById('settings-modal'));
    modal.show();
}

// Cargar configuración guardada
function loadSettings() {
    const saved = localStorage.getItem('trainSimulatorDashboardConfig');
    if (saved) {
        try {
            dashboardConfig = { ...dashboardConfig, ...JSON.parse(saved) };
            maxHistoryPoints = dashboardConfig.historyPoints;
        } catch (e) {
            console.warn('Error cargando configuración:', e);
        }
    }
}

// Cargar configuración en la UI
function loadSettingsToUI() {
    try {
        // Verificar que los elementos existen
        const elements = [
            'theme-select', 'animations-toggle', 'update-interval',
            'history-points', 'speed-unit', 'alert-speed-limit',
            'alert-emergency', 'alert-system'
        ];

        let missingElements = [];
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (!element) {
                missingElements.push(id);
                console.error(`❌ Element ${id} not found`);
            }
        });

        if (missingElements.length > 0) {
            console.error('❌ Missing elements:', missingElements);
            return;
        }

        // Cargar valores
        const themeSelect = document.getElementById('theme-select');
        themeSelect.value = dashboardConfig.theme;

        document.getElementById('animations-toggle').checked = dashboardConfig.animations;
        document.getElementById('update-interval').value = dashboardConfig.updateInterval;
        document.getElementById('history-points').value = dashboardConfig.historyPoints;
        document.getElementById('autobrake-by-signal').checked = dashboardConfig.autobrakeBySignal;

        // Cargar configuración de alertas
        const speedLimitAlert = document.getElementById('alert-speed-limit');
        const emergencyAlert = document.getElementById('alert-emergency');
        const systemAlert = document.getElementById('alert-system');

        if (speedLimitAlert) speedLimitAlert.checked = dashboardConfig.alerts?.speedLimit ?? true;
        if (emergencyAlert) emergencyAlert.checked = dashboardConfig.alerts?.emergency ?? true;
        if (systemAlert) systemAlert.checked = dashboardConfig.alerts?.system ?? true;

    } catch (error) {
        console.error('❌ Error loading settings to UI:', error);
    }
}

// Guardar configuración
function saveSettings() {
    // Recopilar configuración actual
    const newConfig = {
        theme: document.getElementById('theme-select').value,
        animations: document.getElementById('animations-toggle').checked,
        updateInterval: parseInt(document.getElementById('update-interval').value),
        historyPoints: parseInt(document.getElementById('history-points').value),
        speedUnit: document.getElementById('speed-unit').value,
        alerts: {
            speedLimit: document.getElementById('alert-speed-limit').checked,
            emergency: document.getElementById('alert-emergency').checked,
            system: document.getElementById('alert-system').checked
        }
        ,autobrakeBySignal: document.getElementById('autobrake-by-signal').checked
    };

    // Validar configuración antes de guardar
    validateAndSaveConfig(newConfig);
}

async function validateAndSaveConfig(config) {
    try {
        const response = await fetch('/api/validate_config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });

        const result = await response.json();

        if (result.valid) {
            // Configuración válida - guardar
            dashboardConfig = config;
            maxHistoryPoints = dashboardConfig.historyPoints;
            localStorage.setItem('trainSimulatorDashboardConfig', JSON.stringify(dashboardConfig));

            // Aplicar cambios
            applyTheme();
            applyAnimations();
            updateRefreshRate();

            // Mostrar mensaje de éxito
            let message = 'Configuración guardada correctamente';
            if (result.warnings && result.warnings.length > 0) {
                message += '\n\nAdvertencias:\n' + result.warnings.join('\n');
            }
            showAlert(message, 'success');

            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('settings-modal'));
            if (modal) {
                modal.hide();
            }
            // Persist autobrakeBySignal to server as well
            try {
                fetch('/api/autobrake', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enabled: dashboardConfig.autobrakeBySignal })
                });
            } catch (e) {
                console.warn('Error persisting autobrake config to server', e);
            }
        } else {
            // Configuración inválida - mostrar errores
            const errorMessage = 'Errores de configuración:\n' + result.errors.join('\n');
            showAlert(errorMessage, 'danger');
        }
    } catch (error) {
        console.error('Error al validar configuración:', error);
        showAlert('Error al validar configuración. Inténtalo de nuevo.', 'danger');
    }
}

// Restaurar configuración predeterminada
function resetSettings() {
    if (confirm('¿Estás seguro de que quieres restaurar la configuración predeterminada?')) {
        localStorage.removeItem('trainSimulatorDashboardConfig');
        dashboardConfig = {
            theme: 'dark',
            animations: true,
            updateInterval: 1000,
            historyPoints: 50,
            speedUnit: 'kmh',
            alerts: {
                speedLimit: true,
                emergency: true,
                system: true
            }
        };
        maxHistoryPoints = dashboardConfig.historyPoints;
        loadSettingsToUI();
        applyTheme();
        applyAnimations();
        updateRefreshRate();
        updateSpeedUnit();
        showAlert('Configuración restaurada', 'info');

        // Cerrar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('settings-modal'));
        if (modal) {
            modal.hide();
        }
    }
}

// Aplicar tema
function applyTheme() {
    const body = document.body;
    body.className = body.className.replace(/theme-\w+/g, '');
    body.classList.add(`theme-${dashboardConfig.theme}`);

    // Aplicar colores específicos según el tema
    const root = document.documentElement;
    switch (dashboardConfig.theme) {
        case 'light':
            root.style.setProperty('--bg-color', '#f8f9fa');
            root.style.setProperty('--text-color', '#212529');
            root.style.setProperty('--card-bg', '#ffffff');
            root.style.setProperty('--border-color', '#dee2e6');
            break;
        case 'blue':
            root.style.setProperty('--bg-color', '#1a1f3a');
            root.style.setProperty('--text-color', '#e3f2fd');
            root.style.setProperty('--card-bg', '#283593');
            root.style.setProperty('--border-color', '#3949ab');
            break;
        case 'green':
            root.style.setProperty('--bg-color', '#0d1b0d');
            root.style.setProperty('--text-color', '#e8f5e8');
            root.style.setProperty('--card-bg', '#1b5e20');
            root.style.setProperty('--border-color', '#2e7d32');
            break;
        default: // dark
            root.style.setProperty('--bg-color', '#121212');
            root.style.setProperty('--text-color', '#ffffff');
            root.style.setProperty('--card-bg', '#1e1e1e');
            root.style.setProperty('--border-color', '#333333');
    }
}

// Aplicar animaciones
function applyAnimations() {
    const body = document.body;
    if (dashboardConfig.animations) {
        body.classList.remove('no-animations');
    } else {
        body.classList.add('no-animations');
    }
}

// Actualizar intervalo de refresco
function updateRefreshRate() {
    if (socket && socket.connected) {
        socket.emit('set_update_interval', dashboardConfig.updateInterval);
    }
}

// Actualizar unidad de velocidad
function updateSpeedUnit() {
    // Actualizar etiqueta del gráfico
    if (speedChart) {
        const unitLabels = {
            'mph': 'Velocidad (mph)',
            'kmh': 'Velocidad (km/h)',
            'ms': 'Velocidad (m/s)'
        };
        speedChart.data.datasets[0].label = unitLabels[dashboardConfig.speedUnit] || 'Velocidad (km/h)';
        speedChart.update();
    }

    // Actualizar etiqueta en el HTML
    const speedLabel = document.getElementById('speed-label');
    if (speedLabel) {
        const unitLabels = {
            'mph': 'Velocidad (mph)',
            'kmh': 'Velocidad (km/h)',
            'ms': 'Velocidad (m/s)'
        };
        speedLabel.textContent = unitLabels[dashboardConfig.speedUnit] || 'Velocidad (km/h)';
    }

    // Actualizar todas las métricas existentes
    updateAllMetrics();
}

// Actualizar alertas activas
function updateActiveAlerts(alertsData) {
    const container = document.getElementById('active-alerts-container');
    const countBadge = document.getElementById('alerts-count');

    if (!container || !countBadge) {
        console.warn('⚠️ Elementos de alertas no encontrados');
        return;
    }

    // Manejar el caso donde alertsData es un objeto con propiedades alerts
    let alerts = [];
    if (Array.isArray(alertsData)) {
        alerts = alertsData;
    } else if (alertsData && typeof alertsData === 'object' && Array.isArray(alertsData.alerts)) {
        alerts = alertsData.alerts;
    } else {
        console.warn('⚠️ alertsData no es un array ni un objeto válido:', typeof alertsData, alertsData);
        alerts = [];
    }

    // Detectar alertas nuevas: crear set de ids actuales
    const currentIds = new Set(alerts.map(a => a.alert_id));

    // Notificar nuevas alertas criticas (persistentes)
    alerts.forEach(alert => {
        if (!knownAlertIds.has(alert.alert_id)) {
            // Alerta nueva
            if (alert.severity === 'critical') {
                // Mostrar notificación persistente
                showAlert(`${alert.title}: ${alert.message}`, 'danger', true);
            } else if (alert.severity === 'high') {
                // Notificar alto nivel de severidad (no persistente)
                showAlert(`${alert.title}: ${alert.message}`, 'warning', false);
            }
            knownAlertIds.add(alert.alert_id);
        }
    });

    // Actualizar contador
    countBadge.textContent = alerts.length;
    countBadge.className = `badge ms-2 ${getAlertBadgeClass(alerts.length)}`;

    if (alerts.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-shield-alt fa-2x mb-3"></i>
                <p>No hay alertas activas</p>
            </div>
        `;
        return;
    }

    // Mostrar alertas activas
    const alertsHtml = alerts.map(alert => `
        <div class="alert alert-${getAlertSeverityClass(alert.severity)} alert-dismissible fade show mb-2" role="alert">
            <div class="d-flex align-items-center">
                <i class="fas ${getAlertIcon(alert.alert_type)} me-2"></i>
                <div class="flex-grow-1">
                    <strong>${alert.title}</strong>
                    <br>
                    <small class="text-muted">${alert.message}</small>
                    <br>
                    <small class="text-muted">${new Date(alert.timestamp).toLocaleString()}</small>
                </div>
                <button class="btn btn-sm btn-outline-secondary ms-2" onclick="acknowledgeAlert('${alert.alert_id}')">
                    <i class="fas fa-check"></i>
                </button>
            </div>
        </div>
    `).join('');

    container.innerHTML = alertsHtml;

    // Limpiar IDs conocidos que ya no están activos (permitir futuras notificaciones)
    const toRemove = [...knownAlertIds].filter(id => !currentIds.has(id));
    toRemove.forEach(id => knownAlertIds.delete(id));
}

// Obtener clase CSS para severidad de alerta
function getAlertSeverityClass(severity) {
    const classes = {
        'low': 'warning',
        'medium': 'info',
        'high': 'warning',
        'critical': 'danger'
    };
    return classes[severity] || 'secondary';
}

// Obtener clase CSS para badge de contador
function getAlertBadgeClass(count) {
    if (count === 0) return 'bg-success';
    if (count <= 2) return 'bg-warning';
    return 'bg-danger';
}

// Obtener icono para tipo de alerta
function getAlertIcon(alertType) {
    const icons = {
        'speed_violation': 'fa-tachometer-alt',
        'anomaly_detected': 'fa-exclamation-triangle',
        'efficiency_drop': 'fa-chart-line',
        'system_error': 'fa-exclamation-circle',
        'performance_degradation': 'fa-cogs',
        'fuel_low': 'fa-gas-pump',
        'overheating': 'fa-thermometer-half'
        ,'brake_pressure_discrepancy': 'fa-exclamation-triangle'
    };
    return icons[alertType] || 'fa-bell';
}

// Reconocer alerta
function acknowledgeAlert(alertId) {
    fetch(`/api/alerts/acknowledge/${alertId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Alerta reconocida', 'success');
        } else {
            showAlert('Error al reconocer alerta', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error de comunicación', 'danger');
    });
}

// Actualizar métricas de rendimiento
function updatePerformanceMetrics(performance) {
    // Latencia
    const latencyValue = document.getElementById('latency-value');
    if (latencyValue && performance.websocket_latency !== undefined) {
        latencyValue.textContent = performance.websocket_latency.toFixed(1) + ' ms';
    }

    // Ratio de compresión
    const compressionValue = document.getElementById('compression-ratio');
    if (compressionValue && performance.compression_ratio !== undefined) {
        compressionValue.textContent = (performance.compression_ratio * 100).toFixed(1) + '%';
    }

    // Cache hit rate
    const cacheValue = document.getElementById('cache-hit-rate');
    if (cacheValue && performance.cache_hit_rate !== undefined) {
        cacheValue.textContent = (performance.cache_hit_rate * 100).toFixed(1) + '%';
    }

    // Frecuencia de actualización
    const updateFreqValue = document.getElementById('update-frequency');
    if (updateFreqValue && performance.update_frequency !== undefined) {
        updateFreqValue.textContent = performance.update_frequency.toFixed(1);
    }
}

// Actualizar estado de reportes
function updateReportsStatus(reports) {
    const container = document.getElementById('reports-status');
    if (!container) return;

    const statusHtml = `
        <div class="row">
            <div class="col-md-4">
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-calendar-day"></i>
                    </div>
                    <div class="metric-value">${reports.daily_reports || 0}</div>
                    <div class="metric-label">Reportes Diarios</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-calendar-week"></i>
                    </div>
                    <div class="metric-value">${reports.weekly_reports || 0}</div>
                    <div class="metric-label">Reportes Semanales</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-calendar-alt"></i>
                    </div>
                    <div class="metric-value">${reports.monthly_reports || 0}</div>
                    <div class="metric-label">Reportes Mensuales</div>
                </div>
            </div>
        </div>
        <div class="mt-3">
            <div class="small text-muted">
                <i class="fas fa-clock me-1"></i>
                Último reporte: ${reports.last_report ? new Date(reports.last_report).toLocaleString() : 'Nunca'}
            </div>
            <div class="small text-muted">
                <i class="fas fa-cog me-1"></i>
                Automatización: ${reports.automation_enabled ? 'Activada' : 'Desactivada'}
            </div>
        </div>
    `;

    container.innerHTML = statusHtml;
}

// Cargar visualizaciones Bokeh
function loadBokehVisualizations() {
    const container = document.getElementById('bokeh-container');
    if (!container) return;

    // Mostrar loading
    container.innerHTML = `
        <div class="text-center text-muted">
            <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
            <p>Cargando visualizaciones Bokeh...</p>
        </div>
    `;

    // Cargar desde el endpoint Bokeh
    fetch('/bokeh')
    .then(response => response.text())
    .then(html => {
        container.innerHTML = html;
    })
    .catch(error => {
        console.error('Error cargando Bokeh:', error);
        container.innerHTML = `
            <div class="text-center text-danger">
                <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                <p>Error al cargar visualizaciones</p>
                <button onclick="loadBokehVisualizations()" class="btn btn-outline-danger">
                    <i class="fas fa-redo me-2"></i>Reintentar
                </button>
            </div>
        `;
    });
}

// Generar reporte
function generateReport() {
    const button = document.getElementById('generate-report');
    if (!button) return;

    // Deshabilitar botón temporalmente
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generando...';

    fetch('/api/reports/generate/performance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Reporte generado exitosamente', 'success');
        } else {
            showAlert('Error al generar reporte', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error de comunicación', 'danger');
    })
    .finally(() => {
        // Rehabilitar botón
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-plus me-2"></i>Generar Reporte';
    });
}

// Ver reportes
function viewReports() {
    // Abrir en nueva ventana o modal
    window.open('/api/reports/status', '_blank');
}

// Actualizar todas las métricas con la nueva unidad
function updateAllMetrics() {
    // Re-actualizar el gráfico con la nueva unidad
    if (speedChart) {
        function convertSpeed(kmhValue) {
            if (dashboardConfig.speedUnit === 'mph') {
                return kmhValue / 1.609344;
            } else if (dashboardConfig.speedUnit === 'ms') {
                return kmhValue / 3.6;
            }
            return kmhValue; // kmh
        }

        speedChart.data.datasets[0].data = telemetryHistory.map(point => convertSpeed(point.speed));
        speedChart.data.datasets[1].data = telemetryHistory.map(point => convertSpeed(point.limit));
        speedChart.data.datasets[2].data = telemetryHistory.map(point => point.predicted !== null ? convertSpeed(point.predicted) : null);
        speedChart.update();
    }
}

// Inicializar configuración al cargar
document.addEventListener('DOMContentLoaded', function() {
    // ... código existente ...
    initializeSettings();
});