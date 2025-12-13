#!/usr/bin/env python3
"""
tsc_integration_optimized.py
Versión optimizada del módulo de integración con Train Simulator Classic
Implementa optimizaciones avanzadas de frecuencia de lectura y rendimiento
"""

import os
import threading
import time
from typing import Any, Dict, Optional


class TSCIntegrationOptimized:
    """Clase optimizada para la integración con Train Simulator Classic."""

    def __init__(self, config_path="config.ini"):
        """Inicializar la integración optimizada."""
        self.config_path = config_path
        self._load_config()

        # Estado del sistema
        self.conectado = False
        self.datos_anteriores = {}
        self.timestamp_ultima_lectura = 0
        self.timestamp_ultimo_cambio_archivo = 0
        self.contador_lecturas = 0
        self.contador_cambios = 0

        # Optimizaciones de frecuencia
        self.intervalo_base = self.config.getfloat(
            "TSC_INTEGRATION", "update_frequency_hz", fallback=10
        )
        self.intervalo_actual = 1.0 / self.intervalo_base  # Convertir Hz a segundos
        self.intervalo_minimo = 0.01  # 100 Hz máximo
        self.intervalo_maximo = 1.0  # 1 Hz mínimo

        # Buffering inteligente
        self.buffer_datos = []
        self.tamano_buffer_max = 10
        self.cache_datos = {}
        self.cache_timeout = 0.1  # 100ms

        # Estadísticas de rendimiento
        self.stats = {
            "lecturas_totales": 0,
            "lecturas_efectivas": 0,
            "tiempo_promedio_lectura": 0,
            "ratio_eficiencia": 0,
            "timestamp_inicio": time.time(),
        }

        # Mapeo de nombres de control a nombres de IA
        self.mapeo_controles = {
            "CurrentSpeed": "velocidad",
            "SpeedoType": "tipo_velocimetro",
            "Acceleration": "aceleracion",
            "Gradient": "pendiente",
            "FuelLevel": "combustible",
            "CurrentSpeedLimit": "limite_velocidad_actual",
            "NextSpeedLimitSpeed": "limite_velocidad_siguiente",
            "NextSpeedLimitDistance": "distancia_limite_siguiente",
            "SimulationTime": "tiempo_simulacion",
        }

        # Mapeo de comandos IA a nombres de control Raildriver
        self.mapeo_comandos = {
            "acelerador": "VirtualThrottle",
            "freno_tren": "TrainBrakeControl",
            "freno_motor": "EngineBrakeControl",
            "freno_dinamico": "VirtualEngineBrakeControl",
            "reverser": "VirtualReverser",
        }

        # Valores anteriores de comandos para evitar envíos innecesarios
        self.comandos_anteriores = {}

        # Hilo de monitoreo de archivos
        self.hilo_monitoreo = None
        self.monitoreo_activo = False
        self.lock = threading.Lock()

    def _load_config(self):
        """Cargar configuración desde archivo."""
        try:
            import configparser

            self.config = configparser.ConfigParser()
            if os.path.exists(self.config_path):
                self.config.read(self.config_path, encoding="utf-8")
            else:
                # Configuración por defecto
                self.config.add_section("TSC_INTEGRATION")
                self.config.set(
                    "TSC_INTEGRATION",
                    "data_file_path",
                    r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt",
                )
                self.config.set(
                    "TSC_INTEGRATION",
                    "command_file_path",
                    r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\SendCommand.txt",
                )
                self.config.set("TSC_INTEGRATION", "update_frequency_hz", "10")
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            # Fallback a configuración hardcoded
            self.ruta_archivo = (
                r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt"
            )
            self.ruta_archivo_comandos = (
                r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\SendCommand.txt"
            )

        self.ruta_archivo = self.config.get(
            "TSC_INTEGRATION",
            "data_file_path",
            fallback=r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt",
        )
        self.ruta_archivo_comandos = self.config.get(
            "TSC_INTEGRATION",
            "command_file_path",
            fallback=r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\SendCommand.txt",
        )

    def _archivo_modificado(self) -> bool:
        """Verificar si el archivo ha sido modificado desde la última lectura."""
        try:
            if not os.path.exists(self.ruta_archivo):
                return False

            timestamp_actual = os.path.getmtime(self.ruta_archivo)
            if timestamp_actual > self.timestamp_ultimo_cambio_archivo:
                self.timestamp_ultimo_cambio_archivo = timestamp_actual
                return True
            return False
        except Exception as e:
            print(f"Error verificando modificación de archivo: {e}")
            return True  # En caso de error, asumir que cambió

    def _ajustar_frecuencia_adaptativa(
        self, velocidad_actual: float, limite_velocidad: float
    ) -> None:
        """Ajustar la frecuencia de lectura basada en el estado del tren."""
        # Frecuencia alta cuando el tren está en movimiento rápido o cerca de límites
        if velocidad_actual > 0.1:  # Tren en movimiento
            # Más frecuencia si está cerca del límite de velocidad
            diferencia_velocidad = abs(velocidad_actual - limite_velocidad)
            if diferencia_velocidad < 5:  # Dentro de 5 mph del límite
                self.intervalo_actual = self.intervalo_minimo  # Máxima frecuencia
            elif diferencia_velocidad < 15:  # Dentro de 15 mph
                self.intervalo_actual = self.intervalo_base / 2  # Frecuencia media-alta
            else:
                self.intervalo_actual = self.intervalo_base  # Frecuencia normal
        else:
            # Frecuencia reducida cuando el tren está detenido
            self.intervalo_actual = self.intervalo_maximo

        # Asegurar límites
        self.intervalo_actual = max(
            self.intervalo_minimo, min(self.intervalo_maximo, self.intervalo_actual)
        )

    def _leer_datos_optimizados(self) -> Optional[Dict[str, Any]]:
        """Leer datos con optimizaciones avanzadas."""
        inicio_lectura = time.time()

        try:
            # Verificar si el archivo existe
            if not os.path.exists(self.ruta_archivo):
                return None

            # Verificar si el archivo ha cambiado
            if not self._archivo_modificado():
                return None  # No leer si no ha cambiado

            # Leer archivo
            with open(self.ruta_archivo, encoding="utf-8") as archivo:
                contenido = archivo.read()

            # Parsear datos
            datos = {}
            lineas = contenido.strip().split("\n")

            for linea in lineas:
                if ":" in linea:
                    clave, valor = linea.split(":", 1)
                    clave = clave.strip()
                    valor = valor.strip()

                    # Intentar convertir a número
                    try:
                        # Manejar casos especiales
                        if clave in ["SimulationTime"]:
                            datos[clave] = float(valor)
                        elif clave in ["SpeedoType"]:
                            datos[clave] = int(float(valor))
                        else:
                            datos[clave] = float(valor)
                    except ValueError:
                        datos[clave] = valor

            # Convertir al formato IA
            datos_ia = self._convertir_a_formato_ia(datos)

            # Actualizar estadísticas
            tiempo_lectura = time.time() - inicio_lectura
            self.stats["lecturas_totales"] += 1
            self.stats["lecturas_efectivas"] += 1
            self.stats["tiempo_promedio_lectura"] = (
                (self.stats["tiempo_promedio_lectura"] * (self.stats["lecturas_totales"] - 1))
                + tiempo_lectura
            ) / self.stats["lecturas_totales"]

            # Calcular ratio de eficiencia
            tiempo_total = time.time() - self.stats["timestamp_inicio"]
            self.stats["ratio_eficiencia"] = self.stats["lecturas_efectivas"] / max(
                1, tiempo_total / self.intervalo_base
            )

            # Ajustar frecuencia adaptativa
            velocidad_actual = datos_ia.get("velocidad", 0)
            limite_actual = datos_ia.get("limite_velocidad_actual", 160)
            self._ajustar_frecuencia_adaptativa(velocidad_actual, limite_actual)

            # Agregar al buffer
            self._agregar_a_buffer(datos_ia)

            return datos_ia

        except Exception as e:
            print(f"Error leyendo datos optimizados: {e}")
            return None

    def _convertir_a_formato_ia(self, datos_raildriver: Dict[str, Any]) -> Dict[str, Any]:
        """Convertir datos del formato Raildriver al formato IA."""
        datos_ia = {
            "timestamp": time.time(),
            "velocidad": 0.0,
            "tipo_velocimetro": 0,
            "aceleracion": 0.0,
            "pendiente": 0.0,
            "combustible": 1.0,
            "limite_velocidad_actual": 160.0,
            "limite_velocidad_siguiente": 160.0,
            "distancia_limite_siguiente": 1000.0,
            "tiempo_simulacion": 0.0,
        }

        # Mapear datos conocidos
        for control_raildriver, campo_ia in self.mapeo_controles.items():
            if control_raildriver in datos_raildriver:
                valor = datos_raildriver[control_raildriver]

                # Conversiones específicas
                if campo_ia == "velocidad":
                    # Convertir m/s a mph si es necesario
                    datos_ia[campo_ia] = abs(valor) * 2.23694  # m/s a mph
                elif campo_ia == "pendiente":
                    # Convertir a ‰
                    datos_ia[campo_ia] = valor * 1000
                else:
                    datos_ia[campo_ia] = valor

        return datos_ia

    def _agregar_a_buffer(self, datos: Dict[str, Any]) -> None:
        """Agregar datos al buffer inteligente."""
        with self.lock:
            self.buffer_datos.append(datos)
            if len(self.buffer_datos) > self.tamano_buffer_max:
                self.buffer_datos.pop(0)

    def _monitoreo_archivo_hilo(self) -> None:
        """Hilo dedicado para monitoreo continuo de archivos."""
        while self.monitoreo_activo:
            try:
                datos = self._leer_datos_optimizados()
                if datos:
                    # Aquí se podría emitir una señal o callback
                    pass
                time.sleep(self.intervalo_actual)
            except Exception as e:
                print(f"Error en hilo de monitoreo: {e}")
                time.sleep(0.1)

    def conectar(self) -> bool:
        """Conectar al sistema TSC con optimizaciones."""
        try:
            if not os.path.exists(self.ruta_archivo):
                print(f"Archivo de datos no encontrado: {self.ruta_archivo}")
                return False

            # Verificar permisos de escritura para comandos
            directorio_comandos = os.path.dirname(self.ruta_archivo_comandos)
            if not os.path.exists(directorio_comandos):
                os.makedirs(directorio_comandos, exist_ok=True)

            # Inicializar timestamp
            if os.path.exists(self.ruta_archivo):
                self.timestamp_ultimo_cambio_archivo = os.path.getmtime(self.ruta_archivo)

            self.conectado = True
            print("✅ Conexión optimizada establecida con Train Simulator Classic")
            return True

        except Exception as e:
            print(f"Error conectando: {e}")
            return False

    def desconectar(self) -> None:
        """Desconectar del sistema TSC."""
        self.monitoreo_activo = False
        if self.hilo_monitoreo and self.hilo_monitoreo.is_alive():
            self.hilo_monitoreo.join(timeout=1.0)

        self.conectado = False
        print("✅ Desconexión completada")

    def leer_datos(self) -> Optional[Dict[str, Any]]:
        """Leer datos con optimizaciones activadas."""
        if not self.conectado:
            return None

        return self._leer_datos_optimizados()

    def iniciar_monitoreo_continuo(self) -> bool:
        """Iniciar monitoreo continuo en hilo separado."""
        if not self.conectado:
            return False

        if self.hilo_monitoreo and self.hilo_monitoreo.is_alive():
            return True

        self.monitoreo_activo = True
        self.hilo_monitoreo = threading.Thread(target=self._monitoreo_archivo_hilo, daemon=True)
        self.hilo_monitoreo.start()

        print("✅ Monitoreo continuo optimizado iniciado")
        return True

    def detener_monitoreo_continuo(self) -> None:
        """Detener monitoreo continuo."""
        self.monitoreo_activo = False
        if self.hilo_monitoreo:
            self.hilo_monitoreo.join(timeout=1.0)
        print("✅ Monitoreo continuo detenido")

    def enviar_comandos(self, comandos: Dict[str, float]) -> bool:
        """Enviar comandos al juego con optimizaciones."""
        if not self.conectado:
            return False

        try:
            # Filtrar solo comandos que han cambiado significativamente
            comandos_filtrados = {}
            umbral_cambio = self.config.getfloat(
                "PERFORMANCE", "min_command_change_threshold", fallback=0.01
            )

            for comando_ia, valor in comandos.items():
                if comando_ia in self.mapeo_comandos:
                    comando_raildriver = self.mapeo_comandos[comando_ia]
                    valor_anterior = self.comandos_anteriores.get(comando_raildriver, 0)

                    if abs(valor - valor_anterior) >= umbral_cambio:
                        comandos_filtrados[comando_raildriver] = valor
                        self.comandos_anteriores[comando_raildriver] = valor

            # Si no hay cambios significativos, no escribir
            if not comandos_filtrados:
                return True

            # Escribir comandos al archivo
            with open(self.ruta_archivo_comandos, "w", encoding="utf-8") as archivo:
                for comando, valor in comandos_filtrados.items():
                    archivo.write(f"{comando}:{valor:.3f}\n")

            return True

        except Exception as e:
            print(f"Error enviando comandos optimizados: {e}")
            return False

    def obtener_estadisticas_rendimiento(self) -> Dict[str, Any]:
        """Obtener estadísticas de rendimiento del sistema optimizado."""
        tiempo_total = time.time() - self.stats["timestamp_inicio"]

        return {
            "tiempo_total_segundos": tiempo_total,
            "lecturas_totales": self.stats["lecturas_totales"],
            "lecturas_efectivas": self.stats["lecturas_efectivas"],
            "tiempo_promedio_lectura_ms": self.stats["tiempo_promedio_lectura"] * 1000,
            "ratio_eficiencia": self.stats["ratio_eficiencia"],
            "frecuencia_actual_hz": 1.0 / self.intervalo_actual,
            "frecuencia_base_hz": self.intervalo_base,
            "buffer_ocupado": len(self.buffer_datos),
            "buffer_maximo": self.tamano_buffer_max,
        }

    def obtener_datos_buffer(self, cantidad: int = 1) -> list:
        """Obtener datos del buffer inteligente."""
        with self.lock:
            if cantidad == 1:
                return self.buffer_datos[-1:] if self.buffer_datos else []
            else:
                return (
                    self.buffer_datos[-cantidad:]
                    if len(self.buffer_datos) >= cantidad
                    else self.buffer_datos.copy()
                )


# Funciones de compatibilidad con la versión anterior
def TSCIntegration():
    """Factory function para mantener compatibilidad."""
    return TSCIntegrationOptimized()
