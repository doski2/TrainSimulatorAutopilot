# Configuración de Desarrollo para DAGs de Airflow

## Problema

Cuando editas los archivos DAG de Airflow en tu entorno local, los linters como
Pylance muestran errores por varias razones, entre ellas:

1. **Apache Airflow no está instalado** en el entorno local
2. **Los plugins personalizados** no están en el PYTHONPATH
3. **Los módulos del proyecto** no están disponibles fuera del contenedor Docker

## Soluciones

### Opción 1: Instalar Airflow Localmente (Recomendado para Desarrollo)

```bash
# Crear entorno virtual
python -m venv venv_airflow
venv_airflow\Scripts\activate  # Windows
# source venv_airflow/bin/activate  # Linux/Mac

# Instalar Airflow y dependencias
pip install apache-airflow==2.8.0
pip install apache-airflow-providers-postgres
pip install psycopg2-binary

# Instalar dependencias del proyecto
pip install -r ../requirements.txt

# Configurar PYTHONPATH
export PYTHONPATH="$PYTHONPATH:/c/Users/doski/TrainSimulatorAutopilot"
# O en Windows:
# set PYTHONPATH=%PYTHONPATH%;C:\Users\doski\TrainSimulatorAutopilot

# Inicializar base de datos local
airflow db init

# Crear usuario admin
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@localhost

# Iniciar webserver (en terminal separado)
airflow webserver --port 8080

# Iniciar scheduler (en terminal separado)
airflow scheduler
```

### Opción 2: Usar Docker para Desarrollo

```bash
# Construir solo la imagen de Airflow
docker-compose -f docker-compose.airflow.yml build airflow-webserver

# Ejecutar contenedor con montaje de volumen para desarrollo
docker run -it \
    -v $(pwd)/airflow/dags:/opt/airflow/dags \
    -v $(pwd)/airflow/plugins:/opt/airflow/plugins \
    -v $(pwd):/opt/airflow/train_simulator \
    -p 8080:8080 \
    train-simulator-airflow:latest \
    bash

# Dentro del contenedor, puedes editar archivos y probar
```

### Opción 3: Configuración de VS Code/Pylance (Temporal)

Si prefieres trabajar con los errores de linting, puedes:

1. **Configurar excepciones en settings.json de VS Code:**

```json
{
    "python.analysis.diagnosticSeverityOverrides": {
        "reportMissingImports": "warning",
        "reportAttributeAccessIssue": "warning"
    },
    "python.analysis.exclude": [
        "**/airflow/dags/**"
    ]
}
```

1. **Añadir type stubs locales:**

```python
# Crear airflow_stubs.py en la raíz del proyecto
class DAG:
    def __init__(self, dag_id: str, **kwargs): ...

class PythonOperator:
    def __init__(self, task_id: str, python_callable, dag=None, **kwargs): ...

class DummyOperator:
    def __init__(self, task_id: str, dag=None, **kwargs): ...

# Y así sucesivamente...
```

## Estructura Recomendada para Desarrollo

```log
airflow/
├── dags/
│   ├── __init__.py
│   ├── base_dag.py          # Clases base y utilidades
│   ├── train_simulator_*.py # DAGs específicos
│   └── dev_utils.py         # Utilidades de desarrollo
├── plugins/
│   ├── __init__.py
│   └── train_simulator_plugin.py
└── tests/
    ├── test_dags.py
    └── test_plugins.py
```

## Tips para Desarrollo

### 1. Validación Local de DAGs

```python
# En un script separado para validar DAGs
from airflow.models import DagBag

def validate_dags():
    dagbag = DagBag(dag_folder='airflow/dags', include_examples=False)

    if dagbag.import_errors:
        print("Errores de importación:")
        for filename, error in dagbag.import_errors.items():
            print(f"  {filename}: {error}")

    print(f"DAGs encontrados: {list(dagbag.dags.keys())}")

    for dag_id, dag in dagbag.dags.items():
        print(f"Validando DAG: {dag_id}")
        # Aquí puedes añadir validaciones personalizadas

if __name__ == "__main__":
    validate_dags()
```

### 2. Testing de DAGs

```python
# test_dag_example.py
import pytest
from datetime import datetime
from airflow import DAG
from train_simulator_custom_demo_dag import dag

def test_dag_structure():
    """Test que valida la estructura del DAG"""
    assert dag is not None
    assert dag.dag_id == 'train_simulator_custom_operators_demo'
    assert len(dag.tasks) > 0

def test_task_dependencies():
    """Test que valida las dependencias entre tareas"""
    # Aquí puedes validar que las dependencias sean correctas
    pass
```

### 3. Configuración de Logging

```python
# En tu DAG
import logging

# Configurar logging específico para el DAG
logger = logging.getLogger(__name__)

def mi_tarea():
    logger.info("Iniciando tarea")
    try:
        # Lógica aquí
        logger.info("Tarea completada exitosamente")
    except Exception as e:
        logger.error(f"Error en tarea: {e}")
        raise
```

## Conclusión

Los errores de Pylance son normales cuando se desarrolla fuera del entorno Docker.
Las importaciones condicionales permiten que el código sea válido tanto en desarrollo
como en producción. Para un desarrollo más cómodo, considera instalar Airflow localmente
o usar la configuración de Docker con montaje de volúmenes.
