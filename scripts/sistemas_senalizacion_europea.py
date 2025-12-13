# sistemas_senalizacion_europea.py
# Implementación de sistemas de señalización y seguridad europeos
# PZB, LZB, AWS, TPWS para rutas europeas en Train Simulator

import logging
import time
from enum import Enum
from typing import Dict, List, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EstadoPZB(Enum):
    """Estados del sistema PZB (Punktförmige Zugbeeinflussung)"""

    INACTIVO = "inactivo"
    ACTIVO = "activo"
    ADVERTENCIA = "advertencia"
    EMERGENCIA = "emergencia"
    BLOQUEADO = "bloqueado"


class ModoPZB(Enum):
    """Modos de operación del PZB"""

    AUS = "aus"  # Apagado
    HALT = "halt"  # Parada
    FAHRT = "fahrt"  # Marcha
    WACH = "wach"  # Vigilancia
    FREI = "frei"  # Libre


class SistemaPZB:
    """
    Implementación del sistema PZB (Punktförmige Zugbeeinflussung)
    Sistema de protección puntual de trenes alemán
    """

    def __init__(self):
        self.estado = EstadoPZB.INACTIVO
        self.modo_actual = ModoPZB.AUS
        self.velocidad_maxima = 0
        self.velocidad_actual = 0
        self.distancia_baliza = float("inf")
        self.tiempo_advertencia = 0
        self.frenado_emergencia_activo = False
        self.confirmacion_conductor = False
        self.baliza_detectada = False

        # Configuración del sistema
        self.config = {
            "tiempo_respuesta_max": 2.5,  # segundos para confirmar advertencia
            "margen_seguridad": 5,  # km/h de margen
            "distancia_frenado_emergencia": 200,  # metros - reducir para ser más restrictivo
            "velocidad_umbral_emergencia": 10,  # km/h para activar freno de emergencia
        }

        logger.info("Sistema PZB inicializado")

    def actualizar_datos_tren(self, velocidad: float, distancia_baliza: float = float("inf")):
        """
        Actualizar datos actuales del tren

        Args:
            velocidad: Velocidad actual en km/h
            distancia_baliza: Distancia a la próxima baliza en metros
        """
        self.velocidad_actual = velocidad
        self.distancia_baliza = distancia_baliza

    def detectar_baliza(self, tipo_baliza: str, velocidad_maxima: int):
        """
        Detectar una baliza PZB y procesar su información

        Args:
            tipo_baliza: Tipo de baliza (HALT, FAHRT, WACH, FREI)
            velocidad_maxima: Velocidad máxima permitida en km/h
        """
        try:
            self.baliza_detectada = True
            self.velocidad_maxima = velocidad_maxima
            self.modo_actual = ModoPZB[tipo_baliza.upper()]
            self.confirmacion_conductor = False
            self.tiempo_advertencia = time.time()

            logger.info(
                f"Baliza PZB detectada: {tipo_baliza}, velocidad máxima: {velocidad_maxima} km/h"
            )

            # Activar advertencia si es necesario
            if self._requiere_confirmacion():
                self.estado = EstadoPZB.ADVERTENCIA
                logger.warning("Advertencia PZB activada - requiere confirmación del conductor")
            else:
                self.estado = EstadoPZB.ACTIVO
                logger.info("Sistema PZB activado automáticamente")

        except KeyError:
            logger.error(f"Tipo de baliza desconocido: {tipo_baliza}")

    def confirmar_conductor(self):
        """Confirmación manual del conductor"""
        if self.estado == EstadoPZB.ADVERTENCIA:
            self.confirmacion_conductor = True
            self.estado = EstadoPZB.ACTIVO
            logger.info("Confirmación del conductor recibida - PZB activado")

    def procesar_logica_seguridad(self) -> Dict:
        """
        Procesar la lógica de seguridad del PZB y generar comandos

        Returns:
            Dict con comandos a ejecutar
        """
        comandos = {
            "freno_emergencia": False,
            "advertencia_sonora": False,
            "advertencia_visual": False,
            "velocidad_maxima": self.velocidad_maxima,
            "estado_pzb": self.estado.value,
        }

        # Verificar condiciones de emergencia
        if self._verificar_condiciones_emergencia():
            comandos["freno_emergencia"] = True
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True
            self.estado = EstadoPZB.EMERGENCIA
            self.frenado_emergencia_activo = True
            logger.critical("EMERGENCIA PZB: Frenado automático activado")

        # Verificar condiciones de advertencia
        elif self._verificar_condiciones_advertencia():
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True
            if self.estado != EstadoPZB.ADVERTENCIA:
                self.estado = EstadoPZB.ADVERTENCIA
                self.tiempo_advertencia = time.time()
                logger.warning("Advertencia PZB: Conductor debe confirmar")

        # Verificar timeout de confirmación
        elif self._verificar_timeout_confirmacion():
            comandos["freno_emergencia"] = True
            comandos["advertencia_sonora"] = True
            self.estado = EstadoPZB.EMERGENCIA
            logger.error("Timeout de confirmación PZB - frenado automático")

        # Sistema operativo normal
        else:
            if self.estado == EstadoPZB.ADVERTENCIA and self.confirmacion_conductor:
                self.estado = EstadoPZB.ACTIVO
            elif self.estado not in [EstadoPZB.EMERGENCIA, EstadoPZB.BLOQUEADO]:
                self.estado = EstadoPZB.ACTIVO

        return comandos

    def _requiere_confirmacion(self) -> bool:
        """Determinar si la baliza actual requiere confirmación del conductor"""
        return self.modo_actual in [ModoPZB.HALT, ModoPZB.WACH]

    def _verificar_condiciones_emergencia(self) -> bool:
        """Verificar si se deben activar medidas de emergencia"""
        if self.velocidad_actual > self.velocidad_maxima + self.config["margen_seguridad"]:
            return True

        if (
            self.distancia_baliza < self.config["distancia_frenado_emergencia"]
            and self.velocidad_actual > self.velocidad_maxima
        ):
            return True

        return False

    def _verificar_condiciones_advertencia(self) -> bool:
        """Verificar si se debe activar advertencia"""
        if not self.baliza_detectada:
            return False

        if self.velocidad_actual > self.velocidad_maxima and not self.confirmacion_conductor:
            return True

        return False

    def _verificar_timeout_confirmacion(self) -> bool:
        """Verificar si ha expirado el tiempo para confirmar advertencia"""
        if self.estado != EstadoPZB.ADVERTENCIA:
            return False

        tiempo_transcurrido = time.time() - self.tiempo_advertencia
        return tiempo_transcurrido > self.config["tiempo_respuesta_max"]

    def reset(self):
        """Reset del sistema PZB"""
        self.estado = EstadoPZB.INACTIVO
        self.modo_actual = ModoPZB.AUS
        self.velocidad_maxima = 0
        self.frenado_emergencia_activo = False
        self.confirmacion_conductor = False
        self.baliza_detectada = False
        logger.info("Sistema PZB reseteado")

    def obtener_estado(self) -> Dict:
        """Obtener estado completo del sistema PZB"""
        return {
            "estado": self.estado.value,
            "modo": self.modo_actual.value,
            "velocidad_maxima": self.velocidad_maxima,
            "velocidad_actual": self.velocidad_actual,
            "distancia_baliza": self.distancia_baliza,
            "confirmacion_conductor": self.confirmacion_conductor,
            "frenado_emergencia": self.frenado_emergencia_activo,
            "baliza_detectada": self.baliza_detectada,
        }


class EstadoLZB(Enum):
    """Estados del sistema LZB (Linienförmige Zugbeeinflussung)"""

    INACTIVO = "inactivo"
    ACTIVO = "activo"
    SUPERVISION = "supervision"
    EMERGENCIA = "emergencia"


class SistemaLZB:
    """
    Implementación del sistema LZB (Linienförmige Zugbeeinflussung)
    Sistema de protección continua de trenes alemán
    """

    def __init__(self):
        self.estado = EstadoLZB.INACTIVO
        self.velocidad_maxima = 0
        self.velocidad_actual = 0
        self.velocidad_objetivo = 0
        self.distancia_restante = float("inf")
        self.curva_actual = None
        self.pendiente_actual = 0
        self.frenado_automatico = False

        # Configuración del sistema
        self.config = {
            "margen_seguridad": 3,  # km/h
            "tiempo_anticipacion_frenado": 30,  # segundos
            "distancia_minima_supervision": 500,  # metros
            "ajuste_pendiente": 2,  # km/h por grado de pendiente
            "ajuste_curva": 5,  # km/h por radio de curva (menor radio = más reducción)
        }

        logger.info("Sistema LZB inicializado")

    def actualizar_datos_tren(self, velocidad: float, posicion: Optional[Dict] = None):
        """
        Actualizar datos del tren y entorno

        Args:
            velocidad: Velocidad actual en km/h
            posicion: Dict con datos de posición (curva, pendiente, etc.)
        """
        self.velocidad_actual = velocidad

        if posicion:
            self.curva_actual = posicion.get("curva_radio")
            self.pendiente_actual = posicion.get("pendiente", 0)
            self.distancia_restante = posicion.get("distancia_senal", float("inf"))

    def recibir_datos_via(self, datos_via: Dict):
        """
        Recibir datos continuos de la vía (velocidad máxima, restricciones, etc.)

        Args:
            datos_via: Dict con información de la vía
        """
        self.velocidad_maxima = datos_via.get("velocidad_maxima", 0)

        # Calcular velocidad objetivo considerando restricciones
        self.velocidad_objetivo = self._calcular_velocidad_objetivo()

        if self.estado == EstadoLZB.INACTIVO:
            self.estado = EstadoLZB.ACTIVO
            logger.info("Sistema LZB activado")

    def procesar_logica_seguridad(self) -> Dict:
        """
        Procesar lógica de seguridad continua del LZB

        Returns:
            Dict con comandos a ejecutar
        """
        comandos = {
            "freno_emergencia": False,
            "ajuste_velocidad": 0,
            "advertencia_sonora": False,
            "advertencia_visual": False,
            "velocidad_objetivo": self.velocidad_objetivo,
            "estado_lzb": self.estado.value,
        }

        # Verificar exceso de velocidad
        if self.velocidad_actual > self.velocidad_objetivo + self.config["margen_seguridad"]:
            if self._debe_frenar_emergencia():
                comandos["freno_emergencia"] = True
                comandos["advertencia_sonora"] = True
                comandos["advertencia_visual"] = True
                self.estado = EstadoLZB.EMERGENCIA
                self.frenado_automatico = True
                logger.critical("LZB: Exceso de velocidad crítico - frenado automático")
            else:
                # Frenado automático gradual
                comandos["ajuste_velocidad"] = -5  # Reducir 5 km/h
                comandos["advertencia_visual"] = True
                self.estado = EstadoLZB.SUPERVISION
                logger.warning("LZB: Exceso de velocidad - ajuste automático")

        elif self.velocidad_actual > self.velocidad_objetivo:
            # Advertencia por exceso de velocidad
            comandos["advertencia_visual"] = True
            self.estado = EstadoLZB.SUPERVISION

        else:
            # Velocidad dentro de límites
            self.estado = EstadoLZB.ACTIVO
            self.frenado_automatico = False

        return comandos

    def _calcular_velocidad_objetivo(self) -> float:
        """Calcular velocidad objetivo considerando todas las restricciones"""
        velocidad_base = self.velocidad_maxima

        # Ajuste por pendiente
        if self.pendiente_actual > 0:  # Subida
            ajuste_pendiente = -abs(self.pendiente_actual) * self.config["ajuste_pendiente"]
        elif self.pendiente_actual < 0:  # Bajada
            ajuste_pendiente = abs(self.pendiente_actual) * self.config["ajuste_pendiente"]
        else:
            ajuste_pendiente = 0

        # Ajuste por curva
        if self.curva_actual and self.curva_actual < 1000:  # Curva cerrada
            ajuste_curva = -self.config["ajuste_curva"] * (1000 / max(self.curva_actual, 100))
        else:
            ajuste_curva = 0

        velocidad_objetivo = velocidad_base + ajuste_pendiente + ajuste_curva
        return max(0, velocidad_objetivo)

    def _debe_frenar_emergencia(self) -> bool:
        """Determinar si se requiere frenado de emergencia"""
        exceso_velocidad = self.velocidad_actual - self.velocidad_objetivo

        # Emergencia si exceso > 10 km/h y distancia crítica
        if (
            exceso_velocidad > 10
            and self.distancia_restante < self.config["distancia_minima_supervision"]
        ):
            return True

        # Emergencia si exceso > 20 km/h
        if exceso_velocidad > 20:
            return True

        return False

    def reset(self):
        """Reset del sistema LZB"""
        self.estado = EstadoLZB.INACTIVO
        self.velocidad_maxima = 0
        self.velocidad_objetivo = 0
        self.frenado_automatico = False
        logger.info("Sistema LZB reseteado")

    def obtener_estado(self) -> Dict:
        """Obtener estado completo del sistema LZB"""
        return {
            "estado": self.estado.value,
            "velocidad_maxima": self.velocidad_maxima,
            "velocidad_objetivo": self.velocidad_objetivo,
            "velocidad_actual": self.velocidad_actual,
            "distancia_restante": self.distancia_restante,
            "curva_actual": self.curva_actual,
            "pendiente_actual": self.pendiente_actual,
            "frenado_automatico": self.frenado_automatico,
        }


class EstadoAWS(Enum):
    """Estados del sistema AWS (Automatic Warning System)"""

    INACTIVO = "inactivo"
    NORMAL = "normal"
    ADVERTENCIA = "advertencia"
    BLOQUEADO = "bloqueado"


class SistemaAWS:
    """
    Implementación del sistema AWS (Automatic Warning System)
    Sistema de advertencia automática británico
    """

    def __init__(self):
        self.estado = EstadoAWS.INACTIVO
        self.senal_actual = "verde"  # verde, amarillo, rojo
        self.velocidad_maxima = 0
        self.velocidad_actual = 0
        self.confirmacion_conductor = False
        self.tiempo_ultima_confirmacion = 0
        self.bloqueo_activo = False

        # Configuración del sistema
        self.config = {
            "tiempo_confirmacion_max": 3.0,  # segundos
            "margen_seguridad": 5,  # km/h
            "velocidad_maxima_rojo": 0,  # km/h para señal roja
            "velocidad_maxima_amarillo": 50,  # km/h para señal amarilla
        }

        logger.info("Sistema AWS inicializado")

    def actualizar_senal(self, senal: str):
        """
        Actualizar la señal actual detectada

        Args:
            senal: Color de la señal (verde, amarillo, rojo)
        """
        senal = senal.lower()
        if senal not in ["verde", "amarillo", "rojo"]:
            logger.error(f"Señal desconocida: {senal}")
            return

        self.senal_actual = senal
        self.confirmacion_conductor = False
        self.tiempo_ultima_confirmacion = time.time()

        # Establecer velocidad máxima según señal
        if senal == "rojo":
            self.velocidad_maxima = self.config["velocidad_maxima_rojo"]
            self.estado = EstadoAWS.ADVERTENCIA
        elif senal == "amarillo":
            self.velocidad_maxima = self.config["velocidad_maxima_amarillo"]
            self.estado = EstadoAWS.ADVERTENCIA
        else:  # verde
            self.velocidad_maxima = float("inf")  # Sin límite
            self.estado = EstadoAWS.NORMAL

        logger.info(
            f"Señal AWS actualizada: {senal}, velocidad máxima: {self.velocidad_maxima} km/h"
        )

    def confirmar_conductor(self):
        """Confirmación del conductor al presionar el botón AWS"""
        self.confirmacion_conductor = True
        self.tiempo_ultima_confirmacion = time.time()

        if self.estado == EstadoAWS.ADVERTENCIA:
            self.estado = EstadoAWS.NORMAL
            logger.info("AWS confirmado por conductor")

    def actualizar_velocidad(self, velocidad: float):
        """Actualizar velocidad actual del tren"""
        self.velocidad_actual = velocidad

    def procesar_logica_seguridad(self) -> Dict:
        """
        Procesar lógica de seguridad del AWS

        Returns:
            Dict con comandos a ejecutar
        """
        comandos = {
            "bloqueo_tren": False,
            "advertencia_sonora": False,
            "advertencia_visual": False,
            "velocidad_maxima": self.velocidad_maxima,
            "estado_aws": self.estado.value,
        }

        # Verificar timeout de confirmación
        if self.estado == EstadoAWS.ADVERTENCIA and not self.confirmacion_conductor:
            tiempo_sin_confirmar = time.time() - self.tiempo_ultima_confirmacion
            if tiempo_sin_confirmar > self.config["tiempo_confirmacion_max"]:
                comandos["bloqueo_tren"] = True
                comandos["advertencia_sonora"] = True
                self.estado = EstadoAWS.BLOQUEADO
                self.bloqueo_activo = True
                logger.critical("AWS: Timeout de confirmación - tren bloqueado")

        # Verificar exceso de velocidad
        elif (
            self.velocidad_maxima != float("inf")
            and self.velocidad_actual > self.velocidad_maxima + self.config["margen_seguridad"]
        ):
            comandos["bloqueo_tren"] = True
            comandos["advertencia_sonora"] = True
            self.estado = EstadoAWS.BLOQUEADO
            self.bloqueo_activo = True
            logger.critical("AWS: Exceso de velocidad - tren bloqueado")

        # Activar advertencias
        if self.estado == EstadoAWS.ADVERTENCIA and not self.confirmacion_conductor:
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True

        return comandos

    def reset_bloqueo(self):
        """Reset del bloqueo AWS (requiere intervención manual)"""
        if self.bloqueo_activo:
            self.bloqueo_activo = False
            self.estado = EstadoAWS.NORMAL
            logger.info("Bloqueo AWS reseteado")

    def obtener_estado(self) -> Dict:
        """Obtener estado completo del sistema AWS"""
        return {
            "estado": self.estado.value,
            "senal_actual": self.senal_actual,
            "velocidad_maxima": self.velocidad_maxima,
            "velocidad_actual": self.velocidad_actual,
            "confirmacion_conductor": self.confirmacion_conductor,
            "bloqueo_activo": self.bloqueo_activo,
        }


class EstadoTPWS(Enum):
    """Estados del sistema TPWS (Train Protection & Warning System)"""

    INACTIVO = "inactivo"
    ACTIVO = "activo"
    OVERSPEED = "overspeed"
    EMERGENCIA = "emergencia"


class SistemaTPWS:
    """
    Implementación del sistema TPWS (Train Protection & Warning System)
    Sistema de protección y advertencia de trenes británico
    """

    def __init__(self):
        self.estado = EstadoTPWS.INACTIVO
        self.velocidad_maxima = 0
        self.velocidad_actual = 0
        self.distancia_frenado = float("inf")
        self.frenado_emergencia_activo = False

        # Configuración del sistema
        self.config = {
            "margen_seguridad": 3,  # km/h
            "distancia_minima_frenado": 200,  # metros para señal roja
            "tiempo_respuesta_minima": 1.5,  # segundos
            "velocidad_maxima_emergencia": 5,  # km/h umbral para activar freno
        }

        logger.info("Sistema TPWS inicializado")

    def actualizar_restriccion(self, velocidad_maxima: float, distancia: float = float("inf")):
        """
        Actualizar restricción de velocidad detectada

        Args:
            velocidad_maxima: Velocidad máxima permitida en km/h
            distancia: Distancia a la restricción en metros
        """
        self.velocidad_maxima = velocidad_maxima
        self.distancia_frenado = distancia

        if self.estado == EstadoTPWS.INACTIVO:
            self.estado = EstadoTPWS.ACTIVO
            logger.info(f"TPWS activado - velocidad máxima: {velocidad_maxima} km/h")

    def actualizar_velocidad(self, velocidad: float):
        """Actualizar velocidad actual del tren"""
        self.velocidad_actual = velocidad

    def procesar_logica_seguridad(self) -> Dict:
        """
        Procesar lógica de seguridad del TPWS

        Returns:
            Dict con comandos a ejecutar
        """
        comandos = {
            "freno_emergencia": False,
            "advertencia_sonora": False,
            "advertencia_visual": False,
            "velocidad_maxima": self.velocidad_maxima,
            "estado_tpws": self.estado.value,
        }

        # Verificar condiciones de overspeed
        if self._es_overspeed_critico():
            comandos["freno_emergencia"] = True
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True
            self.estado = EstadoTPWS.EMERGENCIA
            self.frenado_emergencia_activo = True
            logger.critical("TPWS: Overspeed crítico detectado - frenado automático")

        elif self._es_overspeed_advertencia():
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True
            self.estado = EstadoTPWS.OVERSPEED
            logger.warning("TPWS: Overspeed detectado - advertencia activada")

        else:
            self.estado = EstadoTPWS.ACTIVO
            self.frenado_emergencia_activo = False

        return comandos

    def _es_overspeed_critico(self) -> bool:
        """Determinar si hay overspeed crítico que requiere frenado inmediato"""
        if self.velocidad_actual <= self.config["velocidad_maxima_emergencia"]:
            return False

        exceso = self.velocidad_actual - self.velocidad_maxima

        # Overspeed crítico si exceso > 10 km/h y distancia crítica
        if exceso > 10 and self.distancia_frenado < self.config["distancia_minima_frenado"]:
            return True

        # Overspeed crítico si exceso > 20 km/h
        if exceso > 20:
            return True

        return False

    def _es_overspeed_advertencia(self) -> bool:
        """Determinar si hay overspeed que requiere advertencia"""
        if self.velocidad_maxima == 0:  # Señal roja
            return self.velocidad_actual > self.config["velocidad_maxima_emergencia"]

        exceso = self.velocidad_actual - self.velocidad_maxima
        return exceso > self.config["margen_seguridad"]

    def reset(self):
        """Reset del sistema TPWS"""
        self.estado = EstadoTPWS.INACTIVO
        self.velocidad_maxima = 0
        self.frenado_emergencia_activo = False
        logger.info("Sistema TPWS reseteado")

    def obtener_estado(self) -> Dict:
        """Obtener estado completo del sistema TPWS"""
        return {
            "estado": self.estado.value,
            "velocidad_maxima": self.velocidad_maxima,
            "velocidad_actual": self.velocidad_actual,
            "distancia_frenado": self.distancia_frenado,
            "frenado_emergencia": self.frenado_emergencia_activo,
        }


class GestorSenalizacionEuropea:
    """
    Gestor principal para sistemas de señalización europeos
    Coordina PZB, LZB, AWS y TPWS según la ruta y normativa aplicable
    """

    def __init__(self):
        self.pzb = SistemaPZB()
        self.lzb = SistemaLZB()
        self.aws = SistemaAWS()
        self.tpws = SistemaTPWS()

        self.sistemas_activos = {
            "pzb": False,
            "lzb": False,
            "aws": False,
            "tpws": False,
        }

        self.normativa_actual = None  # 'alemana', 'británica', 'mixta'

        logger.info("Gestor de señalización europea inicializado")

    def configurar_ruta(self, pais: str, sistemas: List[str]):
        """
        Configurar sistemas activos según el país y ruta

        Args:
            pais: País de la ruta ('alemania', 'reino_unido', etc.)
            sistemas: Lista de sistemas a activar
        """
        # Reset todos los sistemas
        for sistema in self.sistemas_activos:
            self.sistemas_activos[sistema] = False

        # Activar sistemas especificados
        for sistema in sistemas:
            if sistema.lower() in self.sistemas_activos:
                self.sistemas_activos[sistema.lower()] = True

        self.normativa_actual = pais.lower()
        logger.info(f"Configuración de ruta: {pais}, sistemas activos: {sistemas}")

    def procesar_datos_tren(self, datos_tren: Dict) -> Dict:
        """
        Procesar datos del tren y generar comandos de seguridad

        Args:
            datos_tren: Dict con datos del tren (velocidad, posición, etc.)

        Returns:
            Dict con comandos consolidados de todos los sistemas
        """
        comandos_consolidados = {
            "freno_emergencia": False,
            "bloqueo_tren": False,
            "advertencia_sonora": False,
            "advertencia_visual": False,
            "ajuste_velocidad": 0,
            "velocidad_maxima": float("inf"),
            "sistemas_activos": self.sistemas_activos.copy(),
        }

        # Procesar cada sistema activo
        if self.sistemas_activos["pzb"]:
            comandos_pzb = self.pzb.procesar_logica_seguridad()
            self._consolidar_comandos(comandos_consolidados, comandos_pzb)

        if self.sistemas_activos["lzb"]:
            comandos_lzb = self.lzb.procesar_logica_seguridad()
            self._consolidar_comandos(comandos_consolidados, comandos_lzb)

        if self.sistemas_activos["aws"]:
            comandos_aws = self.aws.procesar_logica_seguridad()
            self._consolidar_comandos(comandos_consolidados, comandos_aws)

        if self.sistemas_activos["tpws"]:
            comandos_tpws = self.tpws.procesar_logica_seguridad()
            self._consolidar_comandos(comandos_consolidados, comandos_tpws)

        return comandos_consolidados

    def _consolidar_comandos(self, comandos_base: Dict, comandos_nuevos: Dict):
        """Consolidar comandos de diferentes sistemas (lógica OR para seguridad)"""
        # Frenado de emergencia y bloqueo: activar si cualquier sistema lo requiere
        comandos_base["freno_emergencia"] |= comandos_nuevos.get("freno_emergencia", False)
        comandos_base["bloqueo_tren"] |= comandos_nuevos.get("bloqueo_tren", False)

        # Advertencias: activar si cualquier sistema las requiere
        comandos_base["advertencia_sonora"] |= comandos_nuevos.get("advertencia_sonora", False)
        comandos_base["advertencia_visual"] |= comandos_nuevos.get("advertencia_visual", False)

        # Velocidad máxima: tomar el valor más restrictivo
        velocidad_nueva = comandos_nuevos.get("velocidad_maxima", float("inf"))
        if velocidad_nueva < comandos_base["velocidad_maxima"]:
            comandos_base["velocidad_maxima"] = velocidad_nueva

        # Ajuste de velocidad: acumular ajustes
        comandos_base["ajuste_velocidad"] += comandos_nuevos.get("ajuste_velocidad", 0)

    def actualizar_datos_via(self, datos_via: Dict):
        """
        Actualizar datos de la vía para todos los sistemas

        Args:
            datos_via: Dict con datos de la vía (señales, balizas, etc.)
        """
        # Procesar datos para PZB
        if "baliza_pzb" in datos_via and self.sistemas_activos["pzb"]:
            baliza = datos_via["baliza_pzb"]
            self.pzb.detectar_baliza(baliza["tipo"], baliza["velocidad_maxima"])

        # Procesar datos para LZB
        if "datos_lzb" in datos_via and self.sistemas_activos["lzb"]:
            self.lzb.recibir_datos_via(datos_via["datos_lzb"])

        # Procesar datos para AWS
        if "senal_aws" in datos_via and self.sistemas_activos["aws"]:
            self.aws.actualizar_senal(datos_via["senal_aws"])

        # Procesar datos para TPWS
        if "restriccion_tpws" in datos_via and self.sistemas_activos["tpws"]:
            restriccion = datos_via["restriccion_tpws"]
            self.tpws.actualizar_restriccion(
                restriccion["velocidad_maxima"],
                restriccion.get("distancia", float("inf")),
            )

    def confirmar_conductor(self, sistema: Optional[str] = None):
        """
        Confirmación del conductor para sistemas que la requieren

        Args:
            sistema: Sistema específico o None para todos
        """
        if sistema == "pzb" or sistema is None:
            self.pzb.confirmar_conductor()

        if sistema == "aws" or sistema is None:
            self.aws.confirmar_conductor()

    def obtener_estado_completo(self) -> Dict:
        """Obtener estado completo de todos los sistemas"""
        return {
            "normativa_actual": self.normativa_actual,
            "sistemas_activos": self.sistemas_activos,
            "pzb": self.pzb.obtener_estado() if self.sistemas_activos["pzb"] else None,
            "lzb": self.lzb.obtener_estado() if self.sistemas_activos["lzb"] else None,
            "aws": self.aws.obtener_estado() if self.sistemas_activos["aws"] else None,
            "tpws": (self.tpws.obtener_estado() if self.sistemas_activos["tpws"] else None),
        }

    def reset_sistemas(self):
        """Reset de todos los sistemas"""
        self.pzb.reset()
        self.lzb.reset()
        self.aws.reset_bloqueo()
        self.tpws.reset()
        logger.info("Todos los sistemas de señalización reseteados")
