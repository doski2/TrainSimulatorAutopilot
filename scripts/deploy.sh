#!/bin/bash
# deploy.sh - Script de deployment automatizado para Train Simulator Autopilot

set -e  # Salir en caso de error

echo "🚀 Iniciando deployment de Train Simulator Autopilot"
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes coloreados
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar prerrequisitos
check_prerequisites() {
    print_status "Verificando prerrequisitos..."

    # Verificar Python
    if ! command -v python &> /dev/null; then
        print_error "Python no está instalado"
        exit 1
    fi

    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    print_status "Python version: $PYTHON_VERSION"

    # Verificar pip
    if ! command -v pip &> /dev/null; then
        print_error "pip no está instalado"
        exit 1
    fi

    # Verificar git
    if ! command -v git &> /dev/null; then
        print_warning "git no está instalado - se omitirá verificación de repositorio"
    fi
}

# Configurar entorno virtual
setup_virtualenv() {
    print_status "Configurando entorno virtual..."

    if [ ! -d ".venv" ]; then
        python -m venv .venv
        print_status "Entorno virtual creado"
    else
        print_status "Entorno virtual ya existe"
    fi

    # Activar entorno virtual
    source .venv/bin/activate  # Para Linux/Mac
    # Para Windows sería: .venv\Scripts\activate

    print_status "Entorno virtual activado"
}

# Instalar dependencias
install_dependencies() {
    print_status "Instalando dependencias..."

    pip install --upgrade pip
    pip install -r requirements.txt

    print_status "Dependencias instaladas"
}

# Configurar aplicación
configure_app() {
    print_status "Configurando aplicación..."

    # Copiar configuración de ejemplo si no existe
    if [ ! -f "config.ini" ]; then
        if [ -f "config.ini.example" ]; then
            cp config.ini.example config.ini
            print_status "Archivo config.ini creado desde ejemplo"
        else
            print_warning "No se encontró config.ini.example"
        fi
    fi

    # Verificar configuración
    if [ ! -f "config.ini" ]; then
        print_error "Archivo config.ini no encontrado"
        exit 1
    fi

    print_status "Configuración verificada"
}

# Ejecutar tests
run_tests() {
    print_status "Ejecutando tests..."

    if [ -f "pytest.ini" ]; then
        python -m pytest tests/ -v --tb=short
        print_status "Tests ejecutados exitosamente"
    else
        print_warning "Archivo pytest.ini no encontrado - omitiendo tests"
    fi
}

# Construir documentación (opcional)
build_docs() {
    print_status "Construyendo documentación..."

    if [ -f "mkdocs.yml" ]; then
        pip install mkdocs mkdocs-material
        mkdocs build
        print_status "Documentación construida"
    else
        print_warning "mkdocs.yml no encontrado - omitiendo construcción de docs"
    fi
}

# Optimizar aplicación
optimize_app() {
    print_status "Aplicando optimizaciones..."

    # Compilar archivos Python
    python -m compileall .

    # Crear directorio de logs si no existe
    mkdir -p logs

    print_status "Optimizaciones aplicadas"
}

# Crear script de inicio
create_startup_script() {
    print_status "Creando script de inicio..."

    cat > start_production.sh << 'EOF'
#!/bin/bash
# start_production.sh - Script para iniciar la aplicación en producción

echo "🚀 Iniciando Train Simulator Autopilot (Producción)"

# Activar entorno virtual
source .venv/bin/activate

# Variables de entorno para producción
export FLASK_ENV=production
export FLASK_DEBUG=false

# Iniciar aplicación
python web_dashboard.py

EOF

    chmod +x start_production.sh
    print_status "Script de inicio creado: start_production.sh"
}

# Función principal
main() {
    echo "🎯 Train Simulator Autopilot - Deployment Script"
    echo "=============================================="
    echo ""

    check_prerequisites
    setup_virtualenv
    install_dependencies
    configure_app
    run_tests
    build_docs
    optimize_app
    create_startup_script

    echo ""
    print_status "✅ Deployment completado exitosamente!"
    echo ""
    echo "Para iniciar la aplicación en producción:"
    echo "  ./start_production.sh"
    echo ""
    echo "O manualmente:"
    echo "  source .venv/bin/activate"
    echo "  python web_dashboard.py"
    echo ""
    echo "Documentación disponible en: site/index.html"
}

# Manejo de argumentos
case "${1:-}" in
    "test")
        check_prerequisites
        setup_virtualenv
        install_dependencies
        run_tests
        ;;
    "configure")
        configure_app
        ;;
    "docs")
        build_docs
        ;;
    *)
        main
        ;;
esac</content>
<parameter name="filePath">c:\Users\doski\TrainSimulatorAutopilot\scripts\deploy.sh