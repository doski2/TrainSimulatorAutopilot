#!/usr/bin/env python3
"""
logging_config.py
Configuración centralizada del sistema de logging para Train Simulator Autopilot
"""

import logging
import logging.handlers
import sys
from pathlib import Path


class AutopilotLogger:
    """Sistema de logging centralizado para el proyecto."""

    def __init__(self, config_path: str = "config.ini"):
        self.config_path = Path(config_path)
        self.loggers = {}
        self._setup_logging()

    def _setup_logging(self):
        """Configurar el sistema de logging basado en config.ini"""
        try:
            import configparser

            config = configparser.ConfigParser()
            config.read(self.config_path)

            # Configuración general
            log_level = getattr(
                logging, config.get("GENERAL", "log_level", fallback="INFO").upper()
            )
            max_log_size_mb = config.getint("GENERAL", "max_log_size_mb", fallback=10)

            # Configuración de logging específica
            log_file = config.get("LOGGING", "log_file", fallback="data/logs/autopilot.log")
            enable_console = config.getboolean("LOGGING", "enable_console_logging", fallback=True)
            enable_file = config.getboolean("LOGGING", "enable_file_logging", fallback=True)
            log_format = config.get(
                "LOGGING",
                "log_format",
                fallback="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            ).replace("%%", "%")
            date_format = config.get(
                "LOGGING", "date_format", fallback="%Y-%m-%d %H:%M:%S"
            ).replace("%%", "%")
            backup_count = config.getint("LOGGING", "log_backup_count", fallback=5)

            # Crear directorio de logs si no existe
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Configurar el logger raíz
            root_logger = logging.getLogger("autopilot")
            root_logger.setLevel(log_level)

            # Limpiar handlers existentes
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            # Formato del log
            formatter = logging.Formatter(log_format, datefmt=date_format)

            # Handler para consola
            if enable_console:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(log_level)
                console_handler.setFormatter(formatter)
                root_logger.addHandler(console_handler)

            # Handler para archivo con rotación
            if enable_file:
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=max_log_size_mb * 1024 * 1024,  # Convertir MB a bytes
                    backupCount=backup_count,
                )
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)

            self.root_logger = root_logger

        except Exception as e:
            # Fallback a configuración básica si hay error
            logging.basicConfig(
                level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
            )
            logging.error(f"Error configurando logging: {e}")

    def get_logger(self, name: str) -> logging.Logger:
        """Obtener un logger para un módulo específico."""
        if name not in self.loggers:
            self.loggers[name] = logging.getLogger(f"autopilot.{name}")
        return self.loggers[name]

    def set_level(self, level: str):
        """Cambiar el nivel de logging dinámicamente."""
        try:
            log_level = getattr(logging, level.upper())
            self.root_logger.setLevel(log_level)
            for handler in self.root_logger.handlers:
                handler.setLevel(log_level)
        except AttributeError:
            self.root_logger.warning(f"Nivel de logging inválido: {level}")


# Instancia global del logger
logger_instance = None


def get_logger(name: str) -> logging.Logger:
    """Función global para obtener loggers."""
    global logger_instance
    if logger_instance is None:
        logger_instance = AutopilotLogger()
    return logger_instance.get_logger(name)


def setup_logging(config_path: str = "config.ini"):
    """Configurar el sistema de logging."""
    global logger_instance
    logger_instance = AutopilotLogger(config_path)
    return logger_instance
