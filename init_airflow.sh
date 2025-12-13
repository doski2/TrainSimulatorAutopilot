#!/bin/bash
# Script de inicialización para Apache Airflow con Train Simulator Autopilot
# Uso: ./init_airflow.sh

set -e

echo "🚀 Inicializando Apache Airflow para Train Simulator Autopilot..."

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

# Verificar que Docker Compose esté instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

# Crear directorios necesarios
echo "📁 Creando directorios necesarios..."
mkdir -p airflow/logs/scheduler
mkdir -p airflow/logs/webserver
mkdir -p airflow/logs/worker
mkdir -p airflow/backups
mkdir -p airflow/reports
mkdir -p airflow/monitoring
mkdir -p airflow/alerts
mkdir -p airflow/health_checks

# Crear archivo de variables de entorno para Airflow
echo "⚙️ Creando variables de entorno..."
cat > airflow/.env << EOF
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@postgres/airflow
AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
AIRFLOW__CORE__FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__WEBSERVER__RBAC=True
AIRFLOW__WEBSERVER__SECRET_KEY=$(openssl rand -hex 32)
TRAIN_SIMULATOR_PATH=/opt/airflow/train_simulator
EOF

# Construir e iniciar servicios
echo "🐳 Construyendo e iniciando servicios Docker..."
docker-compose -f docker-compose.airflow.yml up -d --build

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté listo..."
sleep 30

# Inicializar base de datos de Airflow
echo "🗄️ Inicializando base de datos de Airflow..."
docker-compose -f docker-compose.airflow.yml exec airflow-webserver airflow db init

# Crear usuario administrador
echo "👤 Creando usuario administrador..."
docker-compose -f docker-compose.airflow.yml exec airflow-webserver \
    airflow users create \
    --username admin \
    --password admin \
    --firstname Train \
    --lastname Simulator \
    --role Admin \
    --email admin@trainsimulator.local

echo "✅ Inicialización completada!"
echo ""
echo "🌐 Interfaz web de Airflow: http://localhost:8080"
echo "👤 Usuario: admin"
echo "🔑 Contraseña: admin"
echo ""
echo "📊 Monitoreo de Celery: http://localhost:5555"
echo ""
echo "Para ver logs en tiempo real:"
echo "  docker-compose -f docker-compose.airflow.yml logs -f"
echo ""
echo "Para detener los servicios:"
echo "  docker-compose -f docker-compose.airflow.yml down"