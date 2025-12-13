#!/usr/bin/env python3
"""
Configuración y Validación del Train Simulator Autopilot
Script para configurar, validar y optimizar el sistema de piloto automático.
"""

import configparser
import logging
import sys
from pathlib import Path

# Importar el sistema de logging centralizado
try:
    from logging_config import get_logger, setup_logging

    setup_logging()
    logger = get_logger(__name__)
except ImportError:
    # Fallback si no se puede importar
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)


class AutopilotConfigurator:
    """Clase para configurar y validar el sistema de piloto automático."""

    def __init__(self, config_path="config.ini"):
        self.config_path = Path(config_path)
        self.config = configparser.ConfigParser()
        self.default_config = self._get_default_config()

    def _get_default_config(self):
        """Retorna la configuración por defecto."""
        return {
            "GENERAL": {
                "debug_mode": "false",
                "log_level": "INFO",
                "max_log_size_mb": "10",
            },
            "TSC_INTEGRATION": {
                "data_file_path": r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt",
                "command_file_path": r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\SendCommand.txt",
                "update_frequency_hz": "10",
                "max_read_attempts": "5",
                "read_timeout_seconds": "1.0",
            },
            "IA_SYSTEM": {
                "max_speed_kmh": "160",
                "min_speed_kmh": "0",
                "brake_safety_margin": "0.1",
                "acceleration_smoothing": "0.8",
                "gradient_compensation_factor": "0.02",
                "curve_brake_threshold": "25",
                "signal_brake_threshold": "50",
                "emergency_stop_distance_m": "100",
            },
        }

    def load_config(self):
        """Carga la configuración desde archivo."""
        if self.config_path.exists():
            self.config.read(self.config_path, encoding="utf-8")
            logger.info(f"Configuración cargada desde {self.config_path}")
        else:
            logger.warning(f"Archivo de configuración no encontrado: {self.config_path}")
            logger.info("Creando configuración por defecto...")
            self.create_default_config()

    def create_default_config(self):
        """Crea archivo de configuración por defecto."""
        for section, options in self.default_config.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for option, value in options.items():
                self.config.set(section, option, value)

        with open(self.config_path, "w", encoding="utf-8") as configfile:
            self.config.write(configfile)

        logger.info(f"Configuración por defecto creada en {self.config_path}")

    def validate_paths(self):
        """Valida que las rutas de archivos existan."""
        logger.info("Validando rutas de archivos...")

        data_path = self.config.get("TSC_INTEGRATION", "data_file_path", fallback="")

        issues = []

        # Verificar directorio base de RailWorks
        railworks_base = Path(data_path).parent.parent if data_path else None
        if railworks_base and not railworks_base.exists():
            issues.append(f"Directorio base de RailWorks no encontrado: {railworks_base}")
            # Intentar encontrar instalación alternativa
            steam_paths = [
                r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks",
                r"C:\Program Files\Steam\steamapps\common\RailWorks",
                r"D:\Steam\steamapps\common\RailWorks",
            ]
            for path in steam_paths:
                if Path(path).exists():
                    logger.info(f"Instalación alternativa encontrada: {path}")
                    break

        # Verificar directorio plugins
        plugins_dir = Path(data_path).parent if data_path else None
        if plugins_dir and not plugins_dir.exists():
            issues.append(f"Directorio plugins no encontrado: {plugins_dir}")

        if issues:
            logger.warning("Problemas encontrados:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("[OK] Todas las rutas son válidas")

        return len(issues) == 0

    def validate_parameters(self):
        """Valida los parámetros de configuración."""
        logger.info("Validando parámetros...")

        issues = []

        # Validar frecuencia de actualización
        freq = self.config.getfloat("TSC_INTEGRATION", "update_frequency_hz", fallback=10)
        if not 1 <= freq <= 100:
            issues.append(f"Frecuencia de actualización inválida: {freq} Hz (debe ser 1-100)")

        # Validar velocidades
        max_speed = self.config.getfloat("IA_SYSTEM", "max_speed_kmh", fallback=160)
        min_speed = self.config.getfloat("IA_SYSTEM", "min_speed_kmh", fallback=0)
        if max_speed <= min_speed:
            issues.append(f"Velocidad máxima ({max_speed}) debe ser mayor que mínima ({min_speed})")

        # Validar márgenes de seguridad
        brake_margin = self.config.getfloat("IA_SYSTEM", "brake_safety_margin", fallback=0.1)
        if not 0 <= brake_margin <= 1:
            issues.append(f"Margen de frenado inválido: {brake_margin} (debe ser 0-1)")

        if issues:
            logger.warning("Problemas de parámetros encontrados:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("[OK] Todos los parámetros son válidos")

        return len(issues) == 0

    def optimize_settings(self):
        """Optimizaciones automáticas de configuración."""
        logger.info("Optimizando configuración...")

        # Detectar hardware para optimizaciones
        import psutil

        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3) if psutil.virtual_memory() else 0

        logger.info(f"Hardware detectado: {cpu_count} CPUs, {memory_gb:.1f} GB RAM")

        # Ajustar frecuencia basada en hardware
        if cpu_count is not None and memory_gb is not None:
            if cpu_count >= 8 and memory_gb >= 16:
                # Hardware potente - mayor frecuencia
                self.config.set("TSC_INTEGRATION", "update_frequency_hz", "20")
                logger.info("Optimización: Frecuencia aumentada a 20 Hz")
            elif cpu_count <= 4 or memory_gb <= 8:
                # Hardware limitado - menor frecuencia
                self.config.set("TSC_INTEGRATION", "update_frequency_hz", "5")
                logger.info("Optimización: Frecuencia reducida a 5 Hz")
        else:
            logger.warning(
                "No se pudo detectar información del hardware, usando configuración por defecto"
            )

        # Guardar optimizaciones
        self.save_config()
        logger.info("✅ Optimizaciones aplicadas")

    def save_config(self):
        """Guarda la configuración actual."""
        with open(self.config_path, "w", encoding="utf-8") as configfile:
            self.config.write(configfile)
        logger.info(f"Configuración guardada en {self.config_path}")

    def show_current_config(self):
        """Muestra la configuración actual."""
        print("\n=== CONFIGURACIÓN ACTUAL ===")
        for section in self.config.sections():
            print(f"\n[{section}]")
            for option, value in self.config.items(section):
                print(f"{option} = {value}")
        print()

    def run_diagnostics(self):
        """Ejecuta diagnóstico completo del sistema."""
        logger.info("Ejecutando diagnóstico completo...")

        results = {
            "config_loaded": False,
            "paths_valid": False,
            "parameters_valid": False,
            "optimization_applied": False,
        }

        # Cargar configuración
        self.load_config()
        results["config_loaded"] = True

        # Validar rutas
        results["paths_valid"] = self.validate_paths()

        # Validar parámetros
        results["parameters_valid"] = self.validate_parameters()

        # Aplicar optimizaciones
        if results["parameters_valid"]:
            self.optimize_settings()
            results["optimization_applied"] = True

        # Resumen
        print("\n=== RESULTADOS DEL DIAGNÓSTICO ===")
        print(f"Configuración cargada: {'✅' if results['config_loaded'] else '❌'}")
        print(f"Rutas válidas: {'✅' if results['paths_valid'] else '❌'}")
        print(f"Parámetros válidos: {'✅' if results['parameters_valid'] else '❌'}")
        print(f"Optimizaciones aplicadas: {'✅' if results['optimization_applied'] else '❌'}")

        all_good = all(results.values())
        print(f"\nEstado general: {'✅ SISTEMA LISTO' if all_good else '⚠️ REVISAR PROBLEMAS'}")

        return results


def main():
    """Función principal."""
    print("🚂 Train Simulator Autopilot - Configurador")
    print("=" * 50)

    configurator = AutopilotConfigurator()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "validate":
            configurator.load_config()
            configurator.validate_paths()
            configurator.validate_parameters()
        elif command == "optimize":
            configurator.load_config()
            configurator.optimize_settings()
        elif command == "show":
            configurator.load_config()
            configurator.show_current_config()
        elif command == "reset":
            configurator.create_default_config()
        else:
            print("Uso: python configurator.py [validate|optimize|show|reset]")
    else:
        # Modo interactivo
        configurator.run_diagnostics()


if __name__ == "__main__":
    main()
