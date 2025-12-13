// web/static/js/dashboard-sd40.js

// Variables globales para SD 40-2
let socket;
let performanceChart;
let telemetryHistory = [];
let maxHistoryPoints = 50;
let engineRunning = false;
let lastChartUpdate = 0;
let chartUpdateThrottle = 500; // Actualizar gráfico cada 500ms máximo
let lastMetricsUpdate = 0;
let metricsUpdateThrottle = 100; // Actualizar métricas cada 100ms máximo

// Configuración específica SD 40-2
let sd40Config = {
    theme: 'dark',
    animations: true,
    updateInterval: 1000,
    tempUnit: 'fahrenheit',
    controlMode: 'manual',
    alerts: {
        overheat: true,
        lowOil: true,
        lowFuel: true,
        emergency: true
    }
};

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    initializeSD40Dashboard();
});

function initializeSD40Dashboard() {
    // Inicializar gráfico de rendimiento
    initializePerformanceChart();

    // Conectar WebSocket
    connectWebSocket();

    // Configurar event listeners
    setupSD40EventListeners();

    // Inicializar configuración
    initializeSD40Settings();

    // Solicitar datos iniciales
    setTimeout(() => {
        if (socket && socket.connected) {
            socket.emit('request_sd40_telemetry');
        }
    }, 1000);
}

function initializePerformanceChart() {
    const ctx = document.getElementById('performanceChart').getContext('2d');

    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'RPM Motor',
                data: [],
                borderColor: '#ff6b35',
                backgroundColor: 'rgba(255, 107, 53, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                yAxisID: 'y'
            }, {
                label: 'Temperatura (°F)',
                data: [],
                borderColor: '#f7931e',
                backgroundColor: 'rgba(247, 147, 30, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.4,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Tiempo'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'RPM'
                    },
                    min: 0,
                    max: 1000
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Temperatura (°F)'
                    },
                    min: 0,
                    max: 300,
                    grid: {
                        drawOnChartArea: false,
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

function connectWebSocket() {
    socket = io();

    socket.on('connect', function() {
        updateConnectionStatus(true);
    });

    socket.on('disconnect', function() {
        updateConnectionStatus(false);
    });

    socket.on('sd40_telemetry', function(data) {
        updateSD40Metrics(data);
        updatePerformanceChart(data);
        addEventLog('Datos de telemetría recibidos', 'info');
    });

    socket.on('sd40_alert', function(alert) {
        handleSD40Alert(alert);
    });

    socket.on('engine_status', function(status) {
        updateEngineStatus(status);
    });
}

function setupSD40EventListeners() {
    // Controles de acelerador
    const throttleControl = document.getElementById('throttle-control');
    throttleControl.addEventListener('input', function() {
        const value = this.value;
        document.getElementById('throttle-value').textContent = value + '%';
        if (socket && socket.connected) {
            socket.emit('set_throttle', parseInt(value));
        }
    });

    // Freno dinámico
    const dynamicBrakeControl = document.getElementById('dynamic-brake-control');
    dynamicBrakeControl.addEventListener('input', function() {
        const value = this.value;
        document.getElementById('dynamic-brake-value').textContent = value + '%';
        if (socket && socket.connected) {
            socket.emit('set_dynamic_brake', parseInt(value));
        }
    });

    // Freno de tren
    const trainBrakeControl = document.getElementById('train-brake-control');
    trainBrakeControl.addEventListener('input', function() {
        const value = this.value;
        document.getElementById('train-brake-value').textContent = value + '%';
        if (socket && socket.connected) {
            socket.emit('set_train_brake', parseInt(value));
        }
    });

    // Reverser
    const reverserControl = document.getElementById('reverser-control');
    reverserControl.addEventListener('change', function() {
        const value = parseInt(this.value);
        if (socket && socket.connected) {
            socket.emit('set_reverser', value);
        }
        addEventLog(`Reverser cambiado a ${value === 1 ? 'Adelante' : value === -1 ? 'Reversa' : 'Neutral'}`, 'info');
    });

    // Botones de control
    document.getElementById('start-engine').addEventListener('click', function() {
        if (socket && socket.connected) {
            socket.emit('start_engine');
            addEventLog('Comando: Iniciar motor', 'success');
        }
    });

    document.getElementById('stop-engine').addEventListener('click', function() {
        if (socket && socket.connected) {
            socket.emit('stop_engine');
            addEventLog('Comando: Detener motor', 'warning');
        }
    });

    document.getElementById('emergency-stop').addEventListener('click', function() {
        if (socket && socket.connected) {
            socket.emit('emergency_stop');
            addEventLog('¡PARADA DE EMERGENCIA ACTIVADA!', 'danger');
        }
    });

    document.getElementById('horn-control').addEventListener('click', function() {
        if (socket && socket.connected) {
            socket.emit('sound_horn');
            addEventLog('Bocina activada', 'info');
        }
    });
}

function updateSD40Metrics(data) {
    const now = Date.now();
    if (now - lastMetricsUpdate < metricsUpdateThrottle) {
        return; // Throttle: no actualizar métricas demasiado frecuentemente
    }
    lastMetricsUpdate = now;

    // Actualizar métricas principales
    document.getElementById('speed-value').textContent = formatNumber(data.speed || 0, 1);
    document.getElementById('engine-temp-value').textContent = formatNumber(data.engineTemp || 0, 0);
    document.getElementById('oil-pressure-value').textContent = formatNumber(data.oilPressure || 0, 1);
    document.getElementById('amps-value').textContent = formatNumber(data.amps || 0, 0);

    // Actualizar métricas adicionales
    document.getElementById('fuel-consumption-value').textContent = formatNumber(data.fuelConsumption || 0, 1);
    document.getElementById('efficiency-value').textContent = formatNumber(data.efficiency || 0, 1);
    document.getElementById('runtime-value').textContent = formatNumber(data.runtime || 0, 1);
    document.getElementById('brake-pressure-value').textContent = formatNumber(data.brakePressure || 0, 1);
    document.getElementById('main-reservoir-pressure-value').textContent = formatNumber(data.presion_deposito_principal || 0, 1);

    // Actualizar estado del sistema
    const fuelPct = data.combustible_porcentaje !== undefined && data.combustible_porcentaje !== null ? data.combustible_porcentaje : null;
    const fuelGal = data.combustible_galones !== undefined && data.combustible_galones !== null ? data.combustible_galones : null;
    if (fuelGal !== null) {
        document.getElementById('fuel-level').textContent = formatNumber(fuelGal || 0, 1) + ' gal';
    } else {
        document.getElementById('fuel-level').textContent = formatNumber(fuelPct || 0, 1) + '%';
    }
    document.getElementById('sand-level').textContent = formatNumber(data.sandLevel || 0, 1) + '%';
    document.getElementById('water-level').textContent = formatNumber(data.waterLevel || 0, 1) + '%';

    // Almacenar en historial
    telemetryHistory.push({
        timestamp: new Date(),
        speed: data.speed || 0,
        engineTemp: data.engineTemp || 0,
        oilPressure: data.oilPressure || 0,
        amps: data.amps || 0,
        rpm: data.rpm || 0,
        fuelConsumption: data.fuelConsumption || 0,
        efficiency: data.efficiency || 0,
        runtime: data.runtime || 0,
        brakePressure: data.brakePressure || 0,
        mainReservoirPressure: data.presion_deposito_principal || 0
    });

    // Limitar historial
    if (telemetryHistory.length > maxHistoryPoints) {
        telemetryHistory.shift();
    }

    // Verificar alertas
    checkSD40Alerts(data);

    // Sincronizar control del freno de tren si la telemetría provee la posición
    try {
        if (data.posicion_freno_tren !== undefined && data.posicion_freno_tren !== null) {
            const posPercent = Math.round((parseFloat(data.posicion_freno_tren) || 0) * 100);
            const trainBrakeSlider = document.getElementById('train-brake-control');
            const trainBrakeValueEl = document.getElementById('train-brake-value');
            if (trainBrakeSlider) trainBrakeSlider.value = posPercent;
            if (trainBrakeValueEl) trainBrakeValueEl.textContent = posPercent + '%';
        }
    } catch (e) {
        // No bloquear si algo falla al sincronizar
        console.debug('Error sincronizando TrainBrakeControl:', e);
    }
}

function updatePerformanceChart(data) {
    if (!performanceChart) return;

    const now = Date.now();
    if (now - lastChartUpdate < chartUpdateThrottle) {
        return; // Throttle: no actualizar demasiado frecuentemente
    }
    lastChartUpdate = now;

    const timeLabel = new Date().toLocaleTimeString();

    // Agregar nuevos datos
    performanceChart.data.labels.push(timeLabel);
    performanceChart.data.datasets[0].data.push(data.rpm || 0);
    performanceChart.data.datasets[1].data.push(data.engineTemp || 0);

    // Limitar puntos
    if (performanceChart.data.labels.length > maxHistoryPoints) {
        performanceChart.data.labels.shift();
        performanceChart.data.datasets[0].data.shift();
        performanceChart.data.datasets[1].data.shift();
    }

    // Usar requestAnimationFrame para actualización suave
    requestAnimationFrame(() => {
        performanceChart.update('none'); // 'none' para mejor rendimiento
    });
}

function updateEngineStatus(status) {
    engineRunning = status.running;
    const statusElement = document.getElementById('engine-status');
    statusElement.textContent = status.running ? 'Encendido' : 'Apagado';
    statusElement.className = status.running ? 'h5 mb-1 text-success' : 'h5 mb-1 text-danger';

    // Actualizar botones
    document.getElementById('start-engine').disabled = status.running;
    document.getElementById('stop-engine').disabled = !status.running;
}

function checkSD40Alerts(data) {
    if (sd40Config.alerts.overheat && data.engineTemp > 250) {
        showAlert(`¡PELIGRO! Temperatura del motor muy alta: ${data.engineTemp}°F`, 'danger');
        addEventLog(`Alerta: Sobrecalentamiento - ${data.engineTemp}°F`, 'danger');
    }

    if (sd40Config.alerts.lowOil && data.oilPressure < 30) {
        showAlert(`¡ADVERTENCIA! Presión de aceite baja: ${data.oilPressure} psi`, 'warning');
        addEventLog(`Alerta: Baja presión de aceite - ${data.oilPressure} psi`, 'warning');
    }

    if (sd40Config.alerts.lowFuel && (fuelPct !== null ? fuelPct : 100) < 15) {
        const fuelDisplayText = (fuelPct !== null ? `${fuelPct}%` : (fuelGal !== null ? `${fuelGal} gal` : 'N/A'));
        showAlert(`¡ADVERTENCIA! Nivel de combustible bajo: ${fuelDisplayText}`, 'warning');
        addEventLog(`Alerta: Combustible bajo - ${data.fuelLevel}%`, 'warning');
    }

    // Nuevas alertas para métricas adicionales
    if (data.fuelConsumption > 5.0) {  // Consumo alto > 5 gal/h
        showAlert(`¡ADVERTENCIA! Consumo de combustible alto: ${data.fuelConsumption} gal/h`, 'warning');
        addEventLog(`Alerta: Alto consumo de combustible - ${data.fuelConsumption} gal/h`, 'warning');
    }

    if (data.efficiency < 100 && data.speed > 10) {  // Eficiencia baja < 100 mpg cuando en movimiento
        showAlert(`¡ADVERTENCIA! Eficiencia baja: ${data.efficiency} mpg`, 'warning');
        addEventLog(`Alerta: Baja eficiencia - ${data.efficiency} mpg`, 'warning');
    }

    if (data.runtime > 8.0) {  // Tiempo de funcionamiento > 8 horas
        showAlert(`¡INFORMACIÓN! Tiempo de funcionamiento prolongado: ${data.runtime} horas`, 'info');
        addEventLog(`Información: Tiempo prolongado de funcionamiento - ${data.runtime} h`, 'info');
    }

    if (data.brakePressure > 80) {  // Presión de freno alta
        showAlert(`¡ADVERTENCIA! Presión de freno alta: ${data.brakePressure} psi`, 'warning');
        addEventLog(`Alerta: Alta presión de freno - ${data.brakePressure} psi`, 'warning');
    }
}

function handleSD40Alert(alert) {
    if (sd40Config.alerts.emergency) {
        showAlert(alert.message, alert.type || 'warning');
        addEventLog(`Alerta del sistema: ${alert.message}`, alert.type || 'warning');
    }
}

function addEventLog(message, type = 'info') {
    const logContainer = document.getElementById('event-log');
    const timestamp = new Date().toLocaleTimeString();
    const iconClass = {
        'info': 'fa-info-circle text-info',
        'success': 'fa-check-circle text-success',
        'warning': 'fa-exclamation-triangle text-warning',
        'danger': 'fa-exclamation-circle text-danger'
    }[type] || 'fa-info-circle text-info';

    const logEntry = document.createElement('div');
    logEntry.className = 'mb-1';
    logEntry.innerHTML = `
        <small class="text-muted">${timestamp}</small>
        <i class="fas ${iconClass} me-1"></i>
        <span>${message}</span>
    `;

    logContainer.appendChild(logEntry);

    // Limitar entradas del log
    while (logContainer.children.length > 20) {
        logContainer.removeChild(logContainer.firstChild);
    }

    // Auto-scroll
    logContainer.scrollTop = logContainer.scrollHeight;
}

// ==================== FUNCIONALIDAD DE CONFIGURACIÓN SD 40-2 ====================

function initializeSD40Settings() {
    loadSD40Settings();
    setupSD40SettingsEventListeners();
    applyTheme();
}

function setupSD40SettingsEventListeners() {
    // Toggle del panel de configuración
    const settingsLink = document.getElementById('settings-link');
    if (settingsLink) {
        settingsLink.addEventListener('click', function(e) {
            e.preventDefault();
            toggleSettingsPanel();
        });
    }

    // Guardar configuración
    const saveBtn = document.getElementById('save-settings');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveSD40Settings);
    }

    // Restaurar configuración
    const resetBtn = document.getElementById('reset-settings');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetSD40Settings);
    }

    // Cambios en tiempo real
    const themeSelect = document.getElementById('theme-select');
    if (themeSelect) {
        themeSelect.addEventListener('change', function() {
            sd40Config.theme = this.value;
            applyTheme();
        });
    }

    const animationsToggle = document.getElementById('animations-toggle');
    if (animationsToggle) {
        animationsToggle.addEventListener('change', function() {
            sd40Config.animations = this.checked;
            applyAnimations();
        });
    }

    const updateInterval = document.getElementById('update-interval');
    if (updateInterval) {
        updateInterval.addEventListener('change', function() {
            sd40Config.updateInterval = parseInt(this.value);
            updateRefreshRate();
        });
    }

    const tempUnit = document.getElementById('temp-unit');
    if (tempUnit) {
        tempUnit.addEventListener('change', function() {
            sd40Config.tempUnit = this.value;
            updateTemperatureUnit();
        });
    }

    const controlMode = document.getElementById('control-mode');
    if (controlMode) {
        controlMode.addEventListener('change', function() {
            sd40Config.controlMode = this.value;
            updateControlMode();
        });
    }
}

function loadSD40Settings() {
    const saved = localStorage.getItem('sd40DashboardConfig');
    if (saved) {
        try {
            sd40Config = { ...sd40Config, ...JSON.parse(saved) };
        } catch (e) {
            console.warn('Error cargando configuración SD 40-2:', e);
        }
    }
}

function loadSettingsToUI() {
    document.getElementById('theme-select').value = sd40Config.theme;
    document.getElementById('animations-toggle').checked = sd40Config.animations;
    document.getElementById('update-interval').value = sd40Config.updateInterval;
    document.getElementById('temp-unit').value = sd40Config.tempUnit;
    document.getElementById('control-mode').value = sd40Config.controlMode;
    document.getElementById('alert-overheat').checked = sd40Config.alerts.overheat;
    document.getElementById('alert-low-oil').checked = sd40Config.alerts.lowOil;
    document.getElementById('alert-low-fuel').checked = sd40Config.alerts.lowFuel;
    document.getElementById('alert-emergency').checked = sd40Config.alerts.emergency;
}

function saveSD40Settings() {
    sd40Config.alerts.overheat = document.getElementById('alert-overheat').checked;
    sd40Config.alerts.lowOil = document.getElementById('alert-low-oil').checked;
    sd40Config.alerts.lowFuel = document.getElementById('alert-low-fuel').checked;
    sd40Config.alerts.emergency = document.getElementById('alert-emergency').checked;

    localStorage.setItem('sd40DashboardConfig', JSON.stringify(sd40Config));
    showAlert('Configuración SD 40-2 guardada correctamente', 'success');
    addEventLog('Configuración guardada', 'success');
}

function resetSD40Settings() {
    if (confirm('¿Estás seguro de que quieres restaurar la configuración predeterminada de SD 40-2?')) {
        localStorage.removeItem('sd40DashboardConfig');
        sd40Config = {
            theme: 'dark',
            animations: true,
            updateInterval: 1000,
            tempUnit: 'fahrenheit',
            controlMode: 'manual',
            alerts: {
                overheat: true,
                lowOil: true,
                lowFuel: true,
                emergency: true
            }
        };
        loadSettingsToUI();
        applyTheme();
        applyAnimations();
        updateRefreshRate();
        updateTemperatureUnit();
        updateControlMode();
        showAlert('Configuración SD 40-2 restaurada', 'info');
        addEventLog('Configuración restaurada a valores predeterminados', 'info');
    }
}

function updateTemperatureUnit() {
    // Actualizar gráfico si es necesario
    if (performanceChart) {
        const unitLabel = sd40Config.tempUnit === 'fahrenheit' ? 'Temperatura (°F)' : 'Temperatura (°C)';
        performanceChart.options.scales.y1.title.text = unitLabel;
        performanceChart.update();
    }
}

function updateControlMode() {
    const mode = sd40Config.controlMode;
    addEventLog(`Modo de control cambiado a: ${mode}`, 'info');

    // Habilitar/deshabilitar controles según el modo
    const manualControls = ['throttle-control', 'dynamic-brake-control', 'train-brake-control', 'reverser-control'];
    const isManual = mode === 'manual';

    manualControls.forEach(id => {
        document.getElementById(id).disabled = !isManual;
    });

    if (socket && socket.connected) {
        socket.emit('set_control_mode', mode);
    }
}

// Funciones compartidas con el dashboard principal
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        statusElement.className = `badge ${connected ? 'bg-success' : 'bg-danger'}`;
        statusElement.innerHTML = `<i class="fas fa-circle"></i> ${connected ? 'Conectado' : 'Desconectado'}`;
    }
}

function showAlert(message, type = 'info') {
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

    // Auto-remover después de 5 segundos
    setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            alertElement.remove();
        }
    }, 5000);
}

function formatNumber(num, decimals = 1) {
    if (num === null || num === undefined) return '--';
    return Number(num).toFixed(decimals);
}

function toggleSettingsPanel() {
    const panel = document.getElementById('settings-panel');
    const isVisible = panel.style.display !== 'none';

    if (isVisible) {
        panel.style.display = 'none';
    } else {
        panel.style.display = 'block';
        loadSettingsToUI();
        panel.scrollIntoView({ behavior: 'smooth' });
    }
}

function applyTheme() {
    const body = document.body;
    body.className = body.className.replace(/theme-\w+/g, '');
    body.classList.add(`theme-${sd40Config.theme}`);
}

function applyAnimations() {
    const body = document.body;
    if (sd40Config.animations) {
        body.classList.remove('no-animations');
    } else {
        body.classList.add('no-animations');
    }
}

function updateRefreshRate() {
    if (socket && socket.connected) {
        socket.emit('set_update_interval', sd40Config.updateInterval);
    }
}