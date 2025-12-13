# Guía para Extender la Integración de Apache Airflow

Esta guía explica cómo extender y personalizar la integración de Apache Airflow
con Train Simulator Autopilot.

## 📋 Estructura de un DAG Típico

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Configuración estándar
default_args = {
    'owner': 'train_simulator_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Definir el DAG
dag = DAG(
    'mi_dag_personalizado',
    default_args=default_args,
    description='Descripción de mi DAG personalizado',
    schedule_interval='@daily',  # CRON expression
    catchup=False,
)

def mi_funcion_personalizada():
    """Función que ejecuta la lógica del negocio"""
    # Importar módulos del proyecto
    import sys
    sys.path.append('/opt/airflow/train_simulator')

    # Tu lógica aquí
    from mi_modulo import MiClase
    instancia = MiClase()
    resultado = instancia.ejecutar_tarea()

    return resultado

# Definir tareas
tarea_principal = PythonOperator(
    task_id='tarea_principal',
    python_callable=mi_funcion_personalizada,
    dag=dag,
)
```

## 🔧 Creando Operadores Personalizados

### Estructura Básica de un Operador

```python
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from typing import Any, Dict, Optional

class MiOperadorPersonalizado(BaseOperator):

    @apply_defaults
    def __init__(
        self,
        mi_parametro: str = "valor_por_defecto",
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.mi_parametro = mi_parametro

    def execute(self, context: Dict[str, Any]) -> Any:
        """Lógica principal del operador"""
        self.log.info(f"Ejecutando con parámetro: {self.mi_parametro}")

        # Tu lógica aquí
        resultado = self._ejecutar_logica()

        return resultado

    def _ejecutar_logica(self):
        """Método auxiliar con la lógica específica"""
        # Implementar lógica específica
        pass
```

### Ejemplo: Operador de Backup de Configuración

```python
class ConfigBackupOperator(BaseOperator):

    @apply_defaults
    def __init__(
        self,
        config_files: list = None,
        backup_dir: str = "/opt/airflow/backups",
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.config_files = config_files or ['config.ini', 'config.ini.production']
        self.backup_dir = backup_dir

    def execute(self, context):
        import shutil
        from datetime import datetime

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{self.backup_dir}/config_backup_{timestamp}"

        for config_file in self.config_files:
            src = f"/opt/airflow/train_simulator/{config_file}"
            dst = f"{backup_path}/{config_file}"

            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                self.log.info(f"Configuración respaldada: {config_file}")

        return backup_path
```

## 📊 Creando Sensores Personalizados

### Sensor para Detectar Archivos de Log Nuevos

```python
from airflow.sensors.base import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
import os
from datetime import datetime, timedelta

class NewLogFileSensor(BaseSensorOperator):

    @apply_defaults
    def __init__(
        self,
        log_directory: str = "/opt/airflow/train_simulator/logs",
        file_pattern: str = "*.log",
        min_age_minutes: int = 5,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.log_directory = log_directory
        self.file_pattern = file_pattern
        self.min_age_minutes = min_age_minutes

    def poke(self, context):
        """Verifica si hay archivos de log nuevos"""
        import glob
        from datetime import datetime

        cutoff_time = datetime.now() - timedelta(minutes=self.min_age_minutes)

        log_files = glob.glob(f"{self.log_directory}/{self.file_pattern}")

        for log_file in log_files:
            if os.path.getmtime(log_file) > cutoff_time.timestamp():
                self.log.info(f"Archivo de log nuevo detectado: {log_file}")
                return True

        return False
```

## 🎯 Integración con el Sistema Train Simulator

### Usando Módulos Existentes

```python
def integrar_con_autopilot():
    """Ejemplo de integración con autopilot_system.py"""
    sys.path.append('/opt/airflow/train_simulator')

    from autopilot_system import AutopilotSystem

    autopilot = AutopilotSystem()
    status = autopilot.get_system_status()

    # Procesar el estado del sistema
    if status['active_routes']:
        print(f"Rutas activas: {len(status['active_routes'])}")
        # Generar reporte o alerta

    return status
```

### Patrón de Integración Recomendado

```python
def wrapper_function():
    """Wrapper que maneja errores y logging"""
    try:
        # Configurar logging
        import logging
        logging.basicConfig(level=logging.INFO)

        # Importar y ejecutar lógica del core system
        sys.path.append('/opt/airflow/train_simulator')

        from mi_modulo_core import MiClaseCore
        instancia = MiClaseCore()

        # Ejecutar con parámetros de Airflow
        resultado = instancia.ejecutar_contexto_airflow(
            execution_date=context['execution_date'],
            dag_run_id=context['dag_run'].run_id
        )

        # Loggear resultado
        logging.info(f"Ejecución completada: {resultado}")

        return resultado

    except Exception as e:
        logging.error(f"Error en ejecución: {e}")
        raise
```

## 🔄 Manejo de Estados y Contextos

### Usando XCom para Comunicación entre Tareas

```python
def tarea_que_guarda_datos(**context):
    """Tarea que guarda datos para otras tareas"""
    datos = {"resultado": "éxito", "timestamp": datetime.now().isoformat()}

    # Guardar en XCom
    context['ti'].xcom_push(key='mi_datos', value=datos)

    return datos

def tarea_que_lee_datos(**context):
    """Tarea que lee datos de tareas anteriores"""
    # Leer de XCom
    datos_previos = context['ti'].xcom_pull(key='mi_datos', task_ids='tarea_anterior')

    if datos_previos:
        print(f"Datos previos: {datos_previos}")
        # Procesar datos...

    return "procesado"
```

### Variables de Airflow

```python
from airflow.models import Variable

def usar_variables_airflow():
    """Ejemplo de uso de Variables de Airflow"""

    # Leer variable
    umbral_cpu = float(Variable.get("cpu_threshold", default_var=80.0))

    # Establecer variable
    Variable.set("ultimo_backup", datetime.now().isoformat())

    return umbral_cpu
```

## 📈 Monitoreo y Alertas Avanzadas

### Integración con Servicios Externos

```python
def enviar_alerta_slack(mensaje, canal="#alertas-train-simulator"):
    """Envía alerta a Slack"""
    import requests
    from airflow.models import Variable

    webhook_url = Variable.get("slack_webhook_url")

    payload = {
        "channel": canal,
        "text": f"🚨 Train Simulator Alert: {mensaje}",
        "username": "Airflow Bot"
    }

    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200

def alerta_rendimiento(**context):
    """Verifica rendimiento y envía alertas si es necesario"""
    # Lógica de verificación de rendimiento
    metricas = verificar_rendimiento_sistema()

    if metricas['cpu_percent'] > 90:
        enviar_alerta_slack(f"CPU alto: {metricas['cpu_percent']}%")

    if metricas['memory_percent'] > 85:
        enviar_alerta_slack(f"Memoria alta: {metricas['memory_percent']}%")
```

## 🧪 Testing de DAGs

### Estructura de Tests

```python
import pytest
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def test_mi_dag():
    """Test básico de un DAG"""
    dag = DAG(
        'test_dag',
        start_date=datetime(2024, 1, 1),
        catchup=False
    )

    task = PythonOperator(
        task_id='test_task',
        python_callable=lambda: "test",
        dag=dag
    )

    assert len(dag.tasks) == 1
    assert dag.tasks[0].task_id == 'test_task'

def test_mi_funcion():
    """Test de la función que ejecuta el DAG"""
    resultado = mi_funcion_personalizada()
    assert resultado is not None
    assert isinstance(resultado, dict)
```

### Ejecutar Tests

```bash
# Ejecutar tests de DAGs
python -m pytest tests/test_dags/ -v

# Ejecutar tests con coverage
python -m pytest tests/test_dags/ --cov=airflow.dags --cov-report=html
```

## 🚀 Despliegue y Escalabilidad

### Configuración Multi-entorno

```python
# config/airflow_config.py
import os

ENV = os.getenv('AIRFLOW_ENV', 'development')

configs = {
    'development': {
        'executor': 'SequentialExecutor',
        'database': 'sqlite:///airflow.db',
        'parallelism': 1,
    },
    'production': {
        'executor': 'CeleryExecutor',
        'database': 'postgresql://user:pass@host:5432/airflow',
        'parallelism': 32,
    }
}

current_config = configs.get(ENV, configs['development'])
```

### Health Checks Avanzados

```python
def health_check_completo():
    """Health check que verifica múltiples componentes"""
    checks = {
        'database': check_database_connection(),
        'external_apis': check_external_apis(),
        'file_system': check_file_system(),
        'memory_usage': check_memory_usage(),
    }

    overall_status = all(check['status'] == 'healthy' for check in checks.values())

    return {
        'overall_status': 'healthy' if overall_status else 'unhealthy',
        'checks': checks,
        'timestamp': datetime.now().isoformat()
    }
```

## 📚 Mejores Prácticas

### 1. Idempotencia

```python
def tarea_idempotente(fecha_ejecucion):
    """Las tareas deben ser idempotentes"""
    # Verificar si ya se ejecutó para esta fecha
    if ya_ejecutado(fecha_ejecucion):
        print("Tarea ya ejecutada, saltando...")
        return

    # Ejecutar lógica
    ejecutar_logica()

    # Marcar como ejecutada
    marcar_ejecutada(fecha_ejecucion)
```

### 2. Logging Estructurado

```python
import logging
import json

def funcion_con_logging_estructurado():
    """Función con logging estructurado"""
    logger = logging.getLogger(__name__)

    # Log estructurado
    logger.info("Iniciando procesamiento", extra={
        'componente': 'procesador_telemetria',
        'operacion': 'inicio',
        'parametros': {'archivo': 'telemetria.json'}
    })

    try:
        # Lógica aquí
        resultado = procesar_datos()
        logger.info("Procesamiento completado", extra={
            'componente': 'procesador_telemetria',
            'operacion': 'completado',
            'resultado': resultado
        })
        return resultado

    except Exception as e:
        logger.error("Error en procesamiento", extra={
            'componente': 'procesador_telemetria',
            'operacion': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        })
        raise
```

### 3. Manejo de Errores Robusto

```python
def funcion_con_reintentos(max_reintentos=3):
    """Función con manejo robusto de errores y reintentos"""
    for intento in range(max_reintentos):
        try:
            return ejecutar_operacion_riesgosa()

        except ExceptionConocida as e:
            if intento == max_reintentos - 1:
                logger.error(f"Error persistente después de {max_reintentos} intentos: {e}")
                raise

            logger.warning(f"Intento {intento + 1} falló, reintentando: {e}")
            time.sleep(2 ** intento)  # Backoff exponencial

        except ExceptionInesperada as e:
            logger.error(f"Error inesperado: {e}")
            raise
```

### 4. Configuración Flexible

```python
def funcion_configurable(**kwargs):
    """Función que acepta configuración flexible"""
    # Valores por defecto
    config = {
        'timeout': 30,
        'retry_count': 3,
        'log_level': 'INFO',
        **kwargs  # Sobrescribir con parámetros proporcionados
    }

    # Configurar logging basado en parámetro
    logging.getLogger().setLevel(getattr(logging, config['log_level']))

    # Usar configuración en la lógica
    return ejecutar_con_config(config)
```

Esta guía proporciona las bases para extender la integración de Airflow.
Cada implementación dependerá de los requisitos particulares del sistema
Train Simulator Autopilot.
