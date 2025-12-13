# 🚀 Guía de Instalación Rápida - Train Simulator Autopilot

## 📋 Requisitos Previos

- **Python 3.8+** instalado
- **Train Simulator Classic** instalado
- **Node.js 16+** (opcional, para app desktop)
- **Raildriver Interface** configurado (recomendado)

## ⚡ Instalación en 5 Minutos

### Paso 1: Descargar y Preparar

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/train-simulator-autopilot.git
cd train-simulator-autopilot

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### Paso 2: Instalar Dependencias

```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Verificar instalación
python -c "import flask, flask_socketio, numpy, pandas; print('✅ Dependencias instaladas')"
```

### Paso 3: Configurar Rutas TSC

```bash
# Ejecutar configurador
python configurator.py

# O configurar manualmente en config.ini:
# data_file_path = C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt
# command_file_path = C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\SendCommand.txt
```

### Paso 4: Verificar Instalación

```bash
# Probar configuración
python test_config.bat

# Debería mostrar: ✅ Configuración correcta
```

### Paso 5: Iniciar Dashboard

```bash
# Iniciar servidor web
python web_dashboard.py

# O usar launcher
iniciar_dashboard.bat
```

## 🌐 Acceder al Dashboard

Una vez iniciado, abrir en navegador:

- **Dashboard Principal**: <http://localhost:5000>
- **Visualizaciones Bokeh**: <http://localhost:5006> (al hacer clic en "Cargar Bokeh")

## 🧪 Verificar Funcionamiento

### Test Básico

```bash
# Probar API de estado
curl http://localhost:5000/api/status

# Debería retornar JSON con status "online"
```

### Test de Telemetría

- Abrir dashboard en navegador
- Verificar que los valores se actualicen cada segundo
- Datos simulados si TSC no está conectado

## 🔧 Solución de Problemas Rápida

### Error: "Integración TSC no disponible"

```bash
# Verificar rutas en config.ini
# Asegurarse de que TSC esté ejecutándose
# Verificar permisos de archivos
```

### Error: "Puerto 5000 ocupado"

```bash
# Cambiar puerto en web_dashboard.py
# O cerrar proceso que usa el puerto
netstat -ano | findstr :5000
```

### Dashboard no carga

```bash
# Verificar firewall/antivirus
# Probar con otro navegador
# Revisar logs en consola del navegador (F12)
```

## 📊 Características Verificadas

Después de la instalación, verificar:

- ✅ **Dashboard Web**: Interfaz moderna y responsiva
- ✅ **Telemetría Real-time**: Actualizaciones cada 100ms
- ✅ **Alertas**: Sistema de alertas funcionales
- ✅ **Reportes**: Generación automática de reportes
- ✅ **Visualizaciones**: Gráficos Bokeh interactivos
- ✅ **Performance**: Monitoreo de latencia y compresión

## 🎯 Próximos Pasos

1. **Configurar Raildriver**: Para control físico
2. **Personalizar Configuración**: Ajustar parámetros en `config.ini`
3. **Explorar Funcionalidades**: Probar todas las características
4. **Revisar Logs**: Monitorear `logs/autopilot.log`

## 📞 Soporte

Si tienes problemas:

1. Revisar [Documentación Completa](./DOCUMENTATION.md)
2. Verificar [Solución de Problemas](./TROUBLESHOOTING.md)
3. Crear issue en GitHub con logs

---

**¡Listo!** Tu Train Simulator Autopilot está instalado y funcionando. 🚂</content>
parameter name="filePath">c:\Users\doski\TrainSimulatorAutopilot\INSTALLATION_GUIDE.md
