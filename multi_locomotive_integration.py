#!/usr/bin/env python3
"""
multi_locomotive_integration.py
Sistema de integración para soporte de múltiples locomotoras en Train Simulator Classic
Permite detectar, monitorear y controlar múltiples locomotoras simultáneamente
"""

import configparser
import os
import threading
import time
from typing import Any, Dict, List


class LocomotiveData:
    """Clase que representa los datos de una locomotora individual."""

    def __init__(self, locomotive_id: str):
        self.id = locomotive_id
        self.datos_actuales = {}
        self.datos_anteriores = {}
        self.timestamp_ultima_actualizacion = 0
        self.activa = True
        self.nombre = f"Locomotora {locomotive_id}"
        self.tipo = "Desconocido"
        self.velocidad_actual = 0.0
        self.limite_velocidad = 160.0
        self.pendiente = 0.0
        self.combustible = 1.0

    def actualizar_datos(self, datos_nuevos: Dict[str, Any]) -> bool:
        """Actualiza los datos de la locomotora. Retorna True si hubo cambios."""
        timestamp_actual = time.time()

        # Verificar si los datos cambiaron significativamente
        cambios_significativos = self._datos_cambiaron(datos_nuevos)

        if cambios_significativos:
            self.datos_anteriores = self.datos_actuales.copy()
            self.datos_actuales = datos_nuevos.copy()
            self.datos_actuales["timestamp"] = timestamp_actual
            self.timestamp_ultima_actualizacion = timestamp_actual

            # Actualizar propiedades específicas
            self._extraer_propiedades_especificas()

            return True

        return False

    def _datos_cambiaron(self, datos_nuevos: Dict[str, Any]) -> bool:
        """Verifica si los datos nuevos son significativamente diferentes."""
        # Comparar velocidad (cambio mínimo de 0.1 mph)
        velocidad_nueva = datos_nuevos.get("velocidad", 0)
        velocidad_anterior = self.datos_actuales.get("velocidad", 0)
        if abs(velocidad_nueva - velocidad_anterior) > 0.1:
            return True

        # Comparar aceleración (cambio mínimo de 0.01 m/s²)
        accel_nueva = datos_nuevos.get("aceleracion", 0)
        accel_anterior = self.datos_actuales.get("aceleracion", 0)
        if abs(accel_nueva - accel_anterior) > 0.01:
            return True

        # Comparar pendiente (cambio mínimo de 0.1‰)
        pend_nueva = datos_nuevos.get("pendiente", 0)
        pend_anterior = self.datos_actuales.get("pendiente", 0)
        if abs(pend_nueva - pend_anterior) > 0.1:
            return True

        return False

    def _extraer_propiedades_especificas(self):
        """Extrae propiedades específicas de los datos actuales."""
        self.velocidad_actual = self.datos_actuales.get("velocidad", 0)
        self.limite_velocidad = self.datos_actuales.get("limite_velocidad_actual", 160)
        self.pendiente = self.datos_actuales.get("pendiente", 0)
        self.combustible = self.datos_actuales.get("combustible", 1)

    def obtener_estado(self) -> Dict[str, Any]:
        """Retorna el estado completo de la locomotora."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "activa": self.activa,
            "timestamp_ultima_actualizacion": self.timestamp_ultima_actualizacion,
            "velocidad_actual": self.velocidad_actual,
            "limite_velocidad": self.limite_velocidad,
            "pendiente": self.pendiente,
            "combustible": self.combustible,
            "datos_actuales": self.datos_actuales,
            "datos_anteriores": self.datos_anteriores,
        }

    def esta_activa(self) -> bool:
        """Verifica si la locomotora está activa (datos recientes)."""
        tiempo_sin_actualizar = time.time() - self.timestamp_ultima_actualizacion
        return tiempo_sin_actualizar < 30  # 30 segundos de timeout


class MultiLocomotiveIntegration:
    """Sistema de integración para múltiples locomotoras."""

    def __init__(self, config_path="config.ini"):
        """Inicializar el sistema multi-locomotora."""
        self.config_path = config_path
        self._load_config()

        # Estado del sistema
        self.conectado = False
        self.locomotoras = {}  # Dict[str, LocomotiveData]
        self.locomotora_activa = None  # ID de la locomotora actualmente controlada
        self.timestamp_ultima_lectura = 0
        self.intervalo_lectura = 0.05  # 20 Hz

        # Estadísticas
        self.stats = {
            "lecturas_totales": 0,
            "locomotoras_detectadas": 0,
            "locomotoras_activas": 0,
            "timestamp_inicio": time.time(),
        }

        # Hilos
        self.hilo_monitoreo = None
        self.monitoreo_activo = False
        self.lock = threading.Lock()

        # Mapeo de comandos (igual que antes)
        self.mapeo_comandos = {
            "acelerador": "VirtualThrottle",
            "freno_tren": "TrainBrakeControl",
            "freno_motor": "EngineBrakeControl",
            "freno_dinamico": "VirtualEngineBrakeControl",
            "reverser": "VirtualReverser",
            # Nuevos controles de locomotora
            # Doors controlled by AI in future; omit DoorSwitch mapping
            "luces": "LightSwitch",
            "freno_emergencia": "BrakeControl",
        }

    def _load_config(self):
        """Cargar configuración."""
        try:
            self.config = configparser.ConfigParser()
            if os.path.exists(self.config_path):
                self.config.read(self.config_path, encoding="utf-8")

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
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            # Fallback
            self.ruta_archivo = (
                r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt"
            )
            self.ruta_archivo_comandos = (
                r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\SendCommand.txt"
            )

    def conectar(self) -> bool:
        """Conectar al sistema TSC multi-locomotora."""
        try:
            if not os.path.exists(self.ruta_archivo):
                print(f"Archivo de datos no encontrado: {self.ruta_archivo}")
                return False

            # Crear directorio de comandos si no existe
            directorio_comandos = os.path.dirname(self.ruta_archivo_comandos)
            if not os.path.exists(directorio_comandos):
                os.makedirs(directorio_comandos, exist_ok=True)

            self.conectado = True
            print("✅ Conexión multi-locomotora establecida con Train Simulator Classic")
            return True

        except Exception as e:
            print(f"Error conectando: {e}")
            return False

    def desconectar(self) -> None:
        """Desconectar del sistema."""
        self.monitoreo_activo = False
        if self.hilo_monitoreo and self.hilo_monitoreo.is_alive():
            self.hilo_monitoreo.join(timeout=1.0)

        self.conectado = False
        print("✅ Desconexión multi-locomotora completada")

    def _parsear_datos_multi_locomotora(self, contenido: str) -> Dict[str, Dict[str, Any]]:
        """
        Parsea datos de múltiples locomotoras desde el archivo GetData.txt.
        En TSC, múltiples locomotoras pueden estar diferenciadas por prefijos o contextos.
        """
        datos_por_locomotora = {}

        try:
            lineas = contenido.strip().split("\n")

            # Por ahora, asumimos una sola locomotora (lógica básica)
            # En implementaciones futuras, TSC podría usar prefijos como "Loco1_Velocity", "Loco2_Velocity", etc.
            datos_loco = {}

            for linea in lineas:
                if ":" in linea:
                    clave, valor = linea.split(":", 1)
                    clave = clave.strip()
                    valor = valor.strip()

                    try:
                        # Intentar convertir a número
                        if clave in ["SimulationTime"]:
                            datos_loco[clave] = float(valor)
                        elif clave in ["SpeedoType"]:
                            datos_loco[clave] = int(float(valor))
                        else:
                            datos_loco[clave] = float(valor)
                    except ValueError:
                        datos_loco[clave] = valor

            if datos_loco:
                # Convertir al formato IA
                datos_ia = self._convertir_a_formato_ia(datos_loco)
                datos_por_locomotora["loco_1"] = datos_ia

        except Exception as e:
            print(f"Error parseando datos multi-locomotora: {e}")

        return datos_por_locomotora

    def _convertir_a_formato_ia(self, datos_raildriver: Dict[str, Any]) -> Dict[str, Any]:
        """Convertir datos del formato Raildriver al formato IA."""
        # Mapeo de controles (igual que antes)
        mapeo_controles = {
            "CurrentSpeed": "velocidad",
            "SpeedoType": "tipo_velocimetro",
            "Acceleration": "aceleracion",
            "Gradient": "pendiente",
            # FuelLevel mapping removed
            "CurrentSpeedLimit": "limite_velocidad_actual",
            "NextSpeedLimitSpeed": "limite_velocidad_siguiente",
            "NextSpeedLimitDistance": "distancia_limite_siguiente",
            "SimulationTime": "tiempo_simulacion",
        }

        datos_ia = {
            "timestamp": time.time(),
            "velocidad": 0.0,
            "tipo_velocimetro": 0,
            "aceleracion": 0.0,
            "pendiente": 0.0,
            # combustible removed from multi-locomotive defaults
            "limite_velocidad_actual": 160.0,
            "limite_velocidad_siguiente": 160.0,
            "distancia_limite_siguiente": 1000.0,
            "tiempo_simulacion": 0.0,
        }

        # Mapear datos conocidos
        for control_raildriver, campo_ia in mapeo_controles.items():
            if control_raildriver in datos_raildriver:
                valor = datos_raildriver[control_raildriver]

                if campo_ia == "velocidad":
                    datos_ia[campo_ia] = abs(valor) * 2.23694  # m/s a mph
                elif campo_ia == "pendiente":
                    datos_ia[campo_ia] = valor * 1000  # a ‰
                else:
                    datos_ia[campo_ia] = valor

        return datos_ia

    def _actualizar_locomotoras(self, datos_por_locomotora: Dict[str, Dict[str, Any]]) -> List[str]:
        """Actualiza los datos de todas las locomotoras detectadas."""
        locomotoras_actualizadas = []

        with self.lock:
            for loco_id, datos in datos_por_locomotora.items():
                # Crear locomotora si no existe
                if loco_id not in self.locomotoras:
                    self.locomotoras[loco_id] = LocomotiveData(loco_id)
                    print(f"🆕 Nueva locomotora detectada: {loco_id}")

                # Actualizar datos
                if self.locomotoras[loco_id].actualizar_datos(datos):
                    locomotoras_actualizadas.append(loco_id)

            # Limpiar locomotoras inactivas
            self._limpiar_locomotoras_inactivas()

        return locomotoras_actualizadas

    def _limpiar_locomotoras_inactivas(self):
        """Elimina locomotoras que no han sido actualizadas recientemente."""
        locomotoras_a_eliminar = []

        for loco_id, locomotora in self.locomotoras.items():
            if not locomotora.esta_activa():
                locomotoras_a_eliminar.append(loco_id)

        for loco_id in locomotoras_a_eliminar:
            print(f"🗑️ Locomotora inactiva eliminada: {loco_id}")
            del self.locomotoras[loco_id]

    def leer_datos_todas_locomotoras(self) -> Dict[str, Dict[str, Any]]:
        """Lee datos de todas las locomotoras disponibles."""
        if not self.conectado:
            return {}

        try:
            # Leer archivo
            with open(self.ruta_archivo, encoding="utf-8") as archivo:
                contenido = archivo.read()

            # Parsear datos multi-locomotora
            datos_por_locomotora = self._parsear_datos_multi_locomotora(contenido)

            # Actualizar locomotoras
            locomotoras_actualizadas = self._actualizar_locomotoras(datos_por_locomotora)

            # Actualizar estadísticas
            self.stats["lecturas_totales"] += 1
            self.stats["locomotoras_detectadas"] = len(datos_por_locomotora)
            self.stats["locomotoras_activas"] = len(self.locomotoras)

            # Retornar solo datos de locomotoras actualizadas
            resultado = {}
            for loco_id in locomotoras_actualizadas:
                if loco_id in self.locomotoras:
                    resultado[loco_id] = self.locomotoras[loco_id].obtener_estado()

            return resultado

        except Exception as e:
            print(f"Error leyendo datos multi-locomotora: {e}")
            return {}

    def seleccionar_locomotora_activa(self, locomotive_id: str) -> bool:
        """Selecciona qué locomotora controlar activamente."""
        if locomotive_id in self.locomotoras:
            self.locomotora_activa = locomotive_id
            print(f"🎯 Locomotora activa seleccionada: {locomotive_id}")
            return True
        else:
            print(f"❌ Locomotora no encontrada: {locomotive_id}")
            return False

    def enviar_comandos_locomotora(self, locomotive_id: str, comandos: Dict[str, float]) -> bool:
        """Envía comandos a una locomotora específica."""
        if not self.conectado or locomotive_id not in self.locomotoras:
            return False

        try:
            # Por ahora, todos los comandos van al mismo archivo
            # En futuras versiones, podría haber archivos separados por locomotora
            with open(self.ruta_archivo_comandos, "w", encoding="utf-8") as archivo:
                for comando_ia, valor in comandos.items():
                    if comando_ia in self.mapeo_comandos:
                        comando_raildriver = self.mapeo_comandos[comando_ia]
                        archivo.write(f"{comando_raildriver}:{valor:.3f}\n")

            print(f"📡 Comandos enviados a {locomotive_id}: {len(comandos)} controles")
            return True

        except Exception as e:
            print(f"Error enviando comandos a {locomotive_id}: {e}")
            return False

    def obtener_estado_todas_locomotoras(self) -> Dict[str, Dict[str, Any]]:
        """Retorna el estado de todas las locomotoras."""
        with self.lock:
            return {
                loco_id: locomotora.obtener_estado()
                for loco_id, locomotora in self.locomotoras.items()
            }

    def obtener_estadisticas_multi_locomotora(self) -> Dict[str, Any]:
        """Retorna estadísticas del sistema multi-locomotora."""
        tiempo_total = time.time() - self.stats["timestamp_inicio"]

        return {
            "tiempo_total_segundos": tiempo_total,
            "lecturas_totales": self.stats["lecturas_totales"],
            "locomotoras_detectadas": self.stats["locomotoras_detectadas"],
            "locomotoras_activas": len(self.locomotoras),
            "locomotora_activa": self.locomotora_activa,
            "ids_locomotoras": list(self.locomotoras.keys()),
            "conectado": self.conectado,
            "monitoreo_activo": self.monitoreo_activo,
        }

    def iniciar_monitoreo_continuo(self) -> bool:
        """Inicia monitoreo continuo de múltiples locomotoras."""
        if not self.conectado:
            return False

        if self.hilo_monitoreo and self.hilo_monitoreo.is_alive():
            return True

        self.monitoreo_activo = True
        self.hilo_monitoreo = threading.Thread(target=self._hilo_monitoreo_continuo, daemon=True)
        self.hilo_monitoreo.start()

        print("✅ Monitoreo continuo multi-locomotora iniciado")
        return True

    def detener_monitoreo_continuo(self) -> None:
        """Detiene el monitoreo continuo."""
        self.monitoreo_activo = False
        if self.hilo_monitoreo:
            self.hilo_monitoreo.join(timeout=1.0)
        print("✅ Monitoreo continuo multi-locomotora detenido")

    def _hilo_monitoreo_continuo(self):
        """Hilo para monitoreo continuo."""
        while self.monitoreo_activo:
            try:
                datos = self.leer_datos_todas_locomotoras()
                if datos:
                    # Aquí se podrían emitir callbacks o señales
                    pass
                time.sleep(self.intervalo_lectura)
            except Exception as e:
                print(f"Error en monitoreo continuo: {e}")
                time.sleep(0.1)


# Funciones de compatibilidad
def create_multi_locomotive_integration():
    """Factory function para compatibilidad."""
    return MultiLocomotiveIntegration()
