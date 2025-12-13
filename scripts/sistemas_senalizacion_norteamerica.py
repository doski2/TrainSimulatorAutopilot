# sistemas_senalizacion_norteamerica.py
# Implementación de sistemas de señalización y seguridad norteamericanos
# ACSES, PTC, ATC, CAB para rutas norteamericanas en Train Simulator

import logging
import time
from enum import Enum
from typing import Dict, List

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EstadoACSES(Enum):
    """Estados del sistema ACSES (Advanced Civil Speed Enforcement System)"""

    INACTIVO = "inactivo"
    ACTIVO = "activo"
    ENFORCEMENT = "enforcement"
    EMERGENCIA = "emergencia"
    OVERRIDE = "override"


class ModoACSES(Enum):
    """Modos de operación del ACSES"""

    POSITIVE = "positive"  # Velocidad positiva permitida
    RESTRICTED = "restricted"  # Velocidad restringida
    STOP = "stop"  # Parada requerida
    APPROACH = "approach"  # Acercamiento a señal restrictiva


class SistemaACSES:
    """
    Implementación del sistema ACSES (Advanced Civil Speed Enforcement System)
    Sistema de aplicación de velocidad civil avanzada usado por Amtrak
    """

    def __init__(self):
        self.estado = EstadoACSES.INACTIVO
        self.modo_actual = ModoACSES.POSITIVE
        self.velocidad_maxima = 0
        self.velocidad_actual = 0
        self.distancia_proxima = float("inf")
        self.tiempo_ultima_actualizacion = 0
        self.enforcement_activo = False
        self.override_activo = False

        # Configuración del sistema
        self.config = {
            "margen_seguridad": 5,  # km/h
            "tiempo_gracia_enforcement": 10.0,  # segundos para enforcement
            "distancia_minima_enforcement": 1000,  # metros
            "velocidad_maxima_emergencia": 10,  # km/h umbral para activar freno
            "tiempo_override_max": 300.0,  # segundos máximo para override
        }

        logger.info("Sistema ACSES inicializado")

    def actualizar_datos_tren(self, velocidad: float, distancia_proxima: float = float("inf")):
        """
        Actualizar datos actuales del tren

        Args:
            velocidad: Velocidad actual en km/h
            distancia_proxima: Distancia a la próxima restricción en metros
        """
        self.velocidad_actual = velocidad
        self.distancia_proxima = distancia_proxima
        self.tiempo_ultima_actualizacion = time.time()

    def recibir_datos_via(self, datos_via: Dict):
        """
        Recibir datos de la vía del sistema ACSES

        Args:
            datos_via: Dict con información de velocidad y restricciones
        """
        velocidad_maxima = datos_via.get("velocidad_maxima", 0)
        modo = datos_via.get("modo", "positive")

        try:
            self.modo_actual = ModoACSES[modo.upper()]
        except KeyError:
            logger.error(f"Modo ACSES desconocido: {modo}")
            return

        self.velocidad_maxima = velocidad_maxima

        if self.estado == EstadoACSES.INACTIVO:
            self.estado = EstadoACSES.ACTIVO
            logger.info(f"ACSES activado - Modo: {modo}, Velocidad máxima: {velocidad_maxima} km/h")

        # Activar enforcement si es necesario
        if self._requiere_enforcement():
            self.estado = EstadoACSES.ENFORCEMENT
            self.enforcement_activo = True
            logger.warning("ACSES: Modo enforcement activado")

    def procesar_logica_seguridad(self) -> Dict:
        """
        Procesar la lógica de seguridad del ACSES y generar comandos

        Returns:
            Dict con comandos a ejecutar
        """
        comandos = {
            "freno_emergencia": False,
            "advertencia_sonora": False,
            "advertencia_visual": False,
            "velocidad_maxima": self.velocidad_maxima,
            "enforcement_activo": self.enforcement_activo,
            "estado_acses": self.estado.value,
        }

        # Verificar condiciones de emergencia
        if self._verificar_condiciones_emergencia():
            comandos["freno_emergencia"] = True
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True
            self.estado = EstadoACSES.EMERGENCIA
            logger.critical("ACSES: EMERGENCIA - Frenado automático activado")

        # Verificar condiciones de enforcement
        elif self._verificar_condiciones_enforcement():
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True
            if self.estado != EstadoACSES.ENFORCEMENT:
                self.estado = EstadoACSES.ENFORCEMENT
                self.enforcement_activo = True
                logger.warning("ACSES: Enforcement activado por exceso de velocidad")

        # Si enforcement está activo, mantener advertencias mientras haya violación
        if self.enforcement_activo and self.velocidad_actual > self.velocidad_maxima:
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True

        # Verificar timeout de datos
        elif self._verificar_timeout_datos():
            comandos["advertencia_visual"] = True
            logger.warning("ACSES: Timeout de datos de vía")

        else:
            # Sistema operativo normal
            if self.estado == EstadoACSES.ENFORCEMENT and not self.enforcement_activo:
                self.estado = EstadoACSES.ACTIVO
            self.enforcement_activo = False

        return comandos

    def activar_override(self):
        """Activar override manual del conductor (solo en casos específicos)"""
        if self.estado in [EstadoACSES.ENFORCEMENT, EstadoACSES.EMERGENCIA]:
            self.override_activo = True
            self.estado = EstadoACSES.OVERRIDE
            logger.info("ACSES: Override activado por conductor")

    def _requiere_enforcement(self) -> bool:
        """Determinar si el modo actual requiere enforcement"""
        return self.modo_actual in [
            ModoACSES.RESTRICTED,
            ModoACSES.APPROACH,
            ModoACSES.STOP,
        ]

    def _verificar_condiciones_emergencia(self) -> bool:
        """Verificar si se deben activar medidas de emergencia"""
        if self.velocidad_actual > self.velocidad_maxima + self.config["margen_seguridad"] * 2:
            return True

        if (
            self.modo_actual == ModoACSES.STOP
            and self.velocidad_actual > self.config["velocidad_maxima_emergencia"]
        ):
            return True

        return False

    def _verificar_condiciones_enforcement(self) -> bool:
        """Verificar si se debe activar enforcement"""
        if (
            not self.enforcement_activo
            and self.velocidad_actual > self.velocidad_maxima + self.config["margen_seguridad"]
        ):
            return True

        if (
            self.modo_actual == ModoACSES.APPROACH
            and self.distancia_proxima < self.config["distancia_minima_enforcement"]
        ):
            return True

        return False

    def _verificar_timeout_datos(self) -> bool:
        """Verificar si ha expirado el tiempo de actualización de datos"""
        tiempo_transcurrido = time.time() - self.tiempo_ultima_actualizacion
        return tiempo_transcurrido > 30.0  # 30 segundos sin actualización

    def reset(self):
        """Reset del sistema ACSES"""
        self.estado = EstadoACSES.INACTIVO
        self.modo_actual = ModoACSES.POSITIVE
        self.velocidad_maxima = 0
        self.enforcement_activo = False
        self.override_activo = False
        logger.info("Sistema ACSES reseteado")

    def obtener_estado(self) -> Dict:
        """Obtener estado completo del sistema ACSES"""
        return {
            "estado": self.estado.value,
            "modo": self.modo_actual.value,
            "velocidad_maxima": self.velocidad_maxima,
            "velocidad_actual": self.velocidad_actual,
            "distancia_proxima": self.distancia_proxima,
            "enforcement_activo": self.enforcement_activo,
            "override_activo": self.override_activo,
        }


class EstadoPTC(Enum):
    """Estados del sistema PTC (Positive Train Control)"""

    INACTIVO = "inactivo"
    ACTIVO = "activo"
    STOP_ENFORCEMENT = "stop_enforcement"
    APPROACH_ENFORCEMENT = "approach_enforcement"
    EMERGENCIA = "emergencia"


class SistemaPTC:
    """
    Implementación del sistema PTC (Positive Train Control)
    Sistema de control positivo de trenes obligatorio en EEUU
    """

    def __init__(self):
        self.estado = EstadoPTC.INACTIVO
        self.velocidad_maxima = 0
        self.velocidad_actual = 0
        self.distancia_autoridad = float("inf")
        self.tiempo_autoridad = float("inf")
        self.stop_location = None
        self.frenado_emergencia_activo = False

        # Configuración del sistema
        self.config = {
            "margen_seguridad": 3,  # km/h
            "tiempo_anticipacion_stop": 60,  # segundos
            "distancia_minima_stop": 500,  # metros
            "velocidad_maxima_emergencia": 5,  # km/h
            "tiempo_gracia_comunicacion": 30.0,  # segundos
        }

        logger.info("Sistema PTC inicializado")

    def actualizar_autoridad(self, autoridad: Dict):
        """
        Actualizar autoridad de movimiento del PTC

        Args:
            autoridad: Dict con límites de velocidad, distancia y tiempo
        """
        self.velocidad_maxima = autoridad.get("velocidad_maxima", 0)
        self.distancia_autoridad = autoridad.get("distancia_maxima", float("inf"))
        self.tiempo_autoridad = autoridad.get("tiempo_maximo", float("inf"))
        self.stop_location = autoridad.get("stop_location")

        if self.estado == EstadoPTC.INACTIVO:
            self.estado = EstadoPTC.ACTIVO
            logger.info(f"PTC activado - Velocidad máxima: {self.velocidad_maxima} km/h")

    def actualizar_velocidad(self, velocidad: float):
        """Actualizar velocidad actual del tren"""
        self.velocidad_actual = velocidad

    def procesar_logica_seguridad(self) -> Dict:
        """
        Procesar lógica de seguridad del PTC

        Returns:
            Dict con comandos a ejecutar
        """
        comandos = {
            "freno_emergencia": False,
            "advertencia_sonora": False,
            "advertencia_visual": False,
            "velocidad_maxima": self.velocidad_maxima,
            "distancia_autoridad": self.distancia_autoridad,
            "estado_ptc": self.estado.value,
        }

        # Verificar violación de autoridad
        if self._violacion_autoridad():
            comandos["freno_emergencia"] = True
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True
            self.estado = EstadoPTC.EMERGENCIA
            self.frenado_emergencia_activo = True
            logger.critical("PTC: Violación de autoridad - frenado automático")

        # Verificar approach a stop
        elif self._approach_stop():
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True
            self.estado = EstadoPTC.APPROACH_ENFORCEMENT
            logger.warning("PTC: Approach to stop enforcement")

        # Verificar stop enforcement
        elif self._stop_enforcement():
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True
            self.estado = EstadoPTC.STOP_ENFORCEMENT
            logger.warning("PTC: Stop enforcement activado")

        else:
            self.estado = EstadoPTC.ACTIVO
            self.frenado_emergencia_activo = False

        return comandos

    def _violacion_autoridad(self) -> bool:
        """Verificar si hay violación de autoridad de movimiento"""
        # Violación por velocidad
        if self.velocidad_actual > self.velocidad_maxima + self.config["margen_seguridad"]:
            return True

        # Violación por distancia
        if (
            self.distancia_autoridad < 100
            and self.velocidad_actual > self.config["velocidad_maxima_emergencia"]
        ):
            return True

        # Violación por tiempo
        if (
            self.tiempo_autoridad < 30
            and self.velocidad_actual > self.config["velocidad_maxima_emergencia"]
        ):
            return True

        return False

    def _approach_stop(self) -> bool:
        """Verificar si se está acercando a un punto de parada"""
        if self.stop_location and self.distancia_autoridad < self.config["distancia_minima_stop"]:
            return True
        return False

    def _stop_enforcement(self) -> bool:
        """Verificar si se requiere enforcement de parada"""
        if self.stop_location and self.distancia_autoridad < 200:
            return True
        return False

    def reset(self):
        """Reset del sistema PTC"""
        self.estado = EstadoPTC.INACTIVO
        self.velocidad_maxima = 0
        self.distancia_autoridad = float("inf")
        self.tiempo_autoridad = float("inf")
        self.frenado_emergencia_activo = False
        logger.info("Sistema PTC reseteado")

    def obtener_estado(self) -> Dict:
        """Obtener estado completo del sistema PTC"""
        return {
            "estado": self.estado.value,
            "velocidad_maxima": self.velocidad_maxima,
            "velocidad_actual": self.velocidad_actual,
            "distancia_autoridad": self.distancia_autoridad,
            "tiempo_autoridad": self.tiempo_autoridad,
            "stop_location": self.stop_location,
            "frenado_emergencia": self.frenado_emergencia_activo,
        }


class EstadoATC(Enum):
    """Estados del sistema ATC (Automatic Train Control)"""

    INACTIVO = "inactivo"
    ACTIVO = "activo"
    SPEED_ENFORCEMENT = "speed_enforcement"
    SIGNAL_ENFORCEMENT = "signal_enforcement"
    EMERGENCIA = "emergencia"


class SistemaATC:
    """
    Implementación del sistema ATC (Automatic Train Control)
    Sistema de control automático de trenes usado en algunas líneas norteamericanas
    """

    def __init__(self):
        self.estado = EstadoATC.INACTIVO
        self.velocidad_maxima = 0
        self.velocidad_actual = 0
        self.senal_actual = "clear"  # clear, approach, stop
        self.distancia_senal = float("inf")
        self.enforcement_activo = False

        # Configuración del sistema
        self.config = {
            "margen_seguridad": 4,  # km/h
            "distancia_approach": 2000,  # metros para señal approach
            "velocidad_approach": 30,  # km/h para señal approach
            "velocidad_stop": 0,  # km/h para señal stop
            "tiempo_respuesta_max": 5.0,  # segundos
        }

        logger.info("Sistema ATC inicializado")

    def actualizar_senal(self, senal: str, distancia: float = float("inf")):
        """
        Actualizar señal ATC detectada

        Args:
            senal: Tipo de señal (clear, approach, stop)
            distancia: Distancia a la señal en metros
        """
        senal = senal.lower()
        if senal not in ["clear", "approach", "stop"]:
            logger.error(f"Señal ATC desconocida: {senal}")
            return

        self.senal_actual = senal
        self.distancia_senal = distancia

        # Establecer velocidad máxima según señal
        if senal == "stop":
            self.velocidad_maxima = self.config["velocidad_stop"]
        elif senal == "approach":
            self.velocidad_maxima = self.config["velocidad_approach"]
        else:  # clear
            self.velocidad_maxima = float("inf")

        if self.estado == EstadoATC.INACTIVO:
            self.estado = EstadoATC.ACTIVO
            logger.info(
                f"ATC activado - Señal: {senal}, Velocidad máxima: {self.velocidad_maxima} km/h"
            )

    def actualizar_velocidad(self, velocidad: float):
        """Actualizar velocidad actual del tren"""
        self.velocidad_actual = velocidad

    def procesar_logica_seguridad(self) -> Dict:
        """
        Procesar lógica de seguridad del ATC

        Returns:
            Dict con comandos a ejecutar
        """
        comandos = {
            "freno_emergencia": False,
            "advertencia_sonora": False,
            "advertencia_visual": False,
            "velocidad_maxima": self.velocidad_maxima,
            "senal_actual": self.senal_actual,
            "estado_atc": self.estado.value,
        }

        # Verificar violación de velocidad
        if self._violacion_velocidad():
            if self._requiere_frenado_emergencia():
                comandos["freno_emergencia"] = True
                comandos["advertencia_sonora"] = True
                comandos["advertencia_visual"] = True
                self.estado = EstadoATC.EMERGENCIA
                logger.critical("ATC: Violación crítica - frenado automático")
            else:
                comandos["advertencia_sonora"] = True
                comandos["advertencia_visual"] = True
                self.estado = EstadoATC.SPEED_ENFORCEMENT
                self.enforcement_activo = True
                logger.warning("ATC: Enforcement de velocidad activado")

        # Verificar enforcement de señal
        elif self._senal_enforcement():
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True
            self.estado = EstadoATC.SIGNAL_ENFORCEMENT
            logger.warning("ATC: Enforcement de señal activado")

        else:
            self.estado = EstadoATC.ACTIVO
            self.enforcement_activo = False

        return comandos

    def _violacion_velocidad(self) -> bool:
        """Verificar si hay violación de velocidad"""
        if self.velocidad_maxima == float("inf"):
            return False

        return self.velocidad_actual > self.velocidad_maxima + self.config["margen_seguridad"]

    def _requiere_frenado_emergencia(self) -> bool:
        """Determinar si se requiere frenado de emergencia"""
        if self.senal_actual == "stop" and self.velocidad_actual > 10:
            return True

        exceso = self.velocidad_actual - self.velocidad_maxima
        if exceso > 15:  # Exceso mayor a 15 km/h
            return True

        return False

    def _senal_enforcement(self) -> bool:
        """Verificar si se requiere enforcement de señal"""
        if (
            self.senal_actual == "approach"
            and self.distancia_senal < self.config["distancia_approach"]
        ):
            return True

        if self.senal_actual == "stop" and self.distancia_senal < 500:
            return True

        return False

    def reset(self):
        """Reset del sistema ATC"""
        self.estado = EstadoATC.INACTIVO
        self.velocidad_maxima = 0
        self.senal_actual = "clear"
        self.enforcement_activo = False
        logger.info("Sistema ATC reseteado")

    def obtener_estado(self) -> Dict:
        """Obtener estado completo del sistema ATC"""
        return {
            "estado": self.estado.value,
            "senal_actual": self.senal_actual,
            "velocidad_maxima": self.velocidad_maxima,
            "velocidad_actual": self.velocidad_actual,
            "distancia_senal": self.distancia_senal,
            "enforcement_activo": self.enforcement_activo,
        }


class EstadoCAB(Enum):
    """Estados del sistema CAB (Collision Avoidance Braking)"""

    INACTIVO = "inactivo"
    ACTIVO = "activo"
    ALERT = "alert"
    BRAKE = "brake"
    EMERGENCIA = "emergencia"


class SistemaCAB:
    """
    Implementación del sistema CAB (Collision Avoidance Braking)
    Sistema de frenado de evitación de colisiones
    """

    def __init__(self):
        self.estado = EstadoCAB.INACTIVO
        self.velocidad_actual = 0
        self.distancia_adelante = float("inf")
        self.velocidad_adelante = 0
        self.tiempo_colision = float("inf")
        self.alerta_activa = False
        self.frenado_automatico = False

        # Configuración del sistema
        self.config = {
            "distancia_segura_minima": 1000,  # metros
            "tiempo_colision_minimo": 60,  # segundos
            "velocidad_relativa_maxima": 50,  # km/h diferencia máxima segura
            "margen_seguridad": 200,  # metros adicional de seguridad
            "tiempo_respuesta_conductor": 10.0,  # segundos para respuesta
        }

        logger.info("Sistema CAB inicializado")

    def actualizar_datos_tren_adelante(self, distancia: float, velocidad: float):
        """
        Actualizar datos del tren adelante

        Args:
            distancia: Distancia al tren adelante en metros
            velocidad: Velocidad del tren adelante en km/h
        """
        self.distancia_adelante = distancia
        self.velocidad_adelante = velocidad

        # Calcular tiempo estimado de colisión
        velocidad_relativa = self.velocidad_actual - self.velocidad_adelante
        if velocidad_relativa > 0:
            self.tiempo_colision = distancia / (velocidad_relativa * 1000 / 3600)  # Convertir a m/s
        else:
            self.tiempo_colision = float("inf")

        if self.estado == EstadoCAB.INACTIVO:
            self.estado = EstadoCAB.ACTIVO
            logger.info("CAB activado")

    def actualizar_velocidad(self, velocidad: float):
        """Actualizar velocidad actual del tren"""
        self.velocidad_actual = velocidad

    def procesar_logica_seguridad(self) -> Dict:
        """
        Procesar lógica de seguridad del CAB

        Returns:
            Dict con comandos a ejecutar
        """
        comandos = {
            "freno_emergencia": False,
            "advertencia_sonora": False,
            "advertencia_visual": False,
            "alerta_activa": self.alerta_activa,
            "estado_cab": self.estado.value,
        }

        # Verificar riesgo inminente de colisión
        if self._riesgo_colision_critico():
            comandos["freno_emergencia"] = True
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True
            self.estado = EstadoCAB.EMERGENCIA
            self.frenado_automatico = True
            logger.critical("CAB: Riesgo crítico de colisión - frenado automático")

        # Verificar necesidad de frenado automático
        elif self._requiere_frenado_automatico():
            comandos["freno_emergencia"] = True
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True
            self.estado = EstadoCAB.BRAKE
            self.frenado_automatico = True
            logger.critical("CAB: Frenado automático activado")

        # Verificar necesidad de alerta
        elif self._requiere_alerta():
            comandos["advertencia_sonora"] = True
            comandos["advertencia_visual"] = True
            self.estado = EstadoCAB.ALERT
            self.alerta_activa = True
            logger.warning("CAB: Alerta de proximidad activada")

        else:
            self.estado = EstadoCAB.ACTIVO
            self.alerta_activa = False
            self.frenado_automatico = False

        return comandos

    def _riesgo_colision_critico(self) -> bool:
        """Verificar riesgo crítico de colisión"""
        if self.distancia_adelante < 500:  # Menos de 500 metros
            return True

        if self.tiempo_colision < 30:  # Menos de 30 segundos
            return True

        return False

    def _requiere_frenado_automatico(self) -> bool:
        """Verificar si se requiere frenado automático"""
        if self.distancia_adelante < 800 and self.velocidad_actual > self.velocidad_adelante + 20:
            return True

        if self.tiempo_colision < 45:  # Menos de 45 segundos
            return True

        return False

    def _requiere_alerta(self) -> bool:
        """Verificar si se requiere alerta al conductor"""
        if self.distancia_adelante < self.config["distancia_segura_minima"]:
            return True

        if self.tiempo_colision < self.config["tiempo_colision_minimo"]:
            return True

        velocidad_relativa = abs(self.velocidad_actual - self.velocidad_adelante)
        if velocidad_relativa > self.config["velocidad_relativa_maxima"]:
            return True

        return False

    def reset(self):
        """Reset del sistema CAB"""
        self.estado = EstadoCAB.INACTIVO
        self.distancia_adelante = float("inf")
        self.tiempo_colision = float("inf")
        self.alerta_activa = False
        self.frenado_automatico = False
        logger.info("Sistema CAB reseteado")

    def obtener_estado(self) -> Dict:
        """Obtener estado completo del sistema CAB"""
        return {
            "estado": self.estado.value,
            "velocidad_actual": self.velocidad_actual,
            "distancia_adelante": self.distancia_adelante,
            "velocidad_adelante": self.velocidad_adelante,
            "tiempo_colision": self.tiempo_colision,
            "alerta_activa": self.alerta_activa,
            "frenado_automatico": self.frenado_automatico,
        }


class GestorSenalizacionNorteamerica:
    """
    Gestor principal para sistemas de señalización norteamericanos
    Coordina ACSES, PTC, ATC y CAB según la región y normativa aplicable
    """

    def __init__(self):
        self.acses = SistemaACSES()
        self.ptc = SistemaPTC()
        self.atc = SistemaATC()
        self.cab = SistemaCAB()

        self.sistemas_activos = {
            "acses": False,
            "ptc": False,
            "atc": False,
            "cab": False,
        }

        self.region_actual = None  # 'nordeste', 'sur', 'oeste', 'canada'

        logger.info("Gestor de señalización norteamericana inicializado")

    def configurar_region(self, region: str, sistemas: List[str]):
        """
        Configurar sistemas activos según la región

        Args:
            region: Región del sistema ('nordeste', 'sur', 'oeste', 'canada')
            sistemas: Lista de sistemas a activar
        """
        # Reset todos los sistemas
        for sistema in self.sistemas_activos:
            self.sistemas_activos[sistema] = False

        # Activar sistemas especificados
        for sistema in sistemas:
            if sistema.lower() in self.sistemas_activos:
                self.sistemas_activos[sistema.lower()] = True

        self.region_actual = region.lower()
        logger.info(f"Configuración de región: {region}, sistemas activos: {sistemas}")

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
            "advertencia_sonora": False,
            "advertencia_visual": False,
            "velocidad_maxima": float("inf"),
            "sistemas_activos": self.sistemas_activos.copy(),
        }

        # Procesar cada sistema activo
        if self.sistemas_activos["acses"]:
            comandos_acses = self.acses.procesar_logica_seguridad()
            self._consolidar_comandos(comandos_consolidados, comandos_acses)

        if self.sistemas_activos["ptc"]:
            comandos_ptc = self.ptc.procesar_logica_seguridad()
            self._consolidar_comandos(comandos_consolidados, comandos_ptc)

        if self.sistemas_activos["atc"]:
            comandos_atc = self.atc.procesar_logica_seguridad()
            self._consolidar_comandos(comandos_consolidados, comandos_atc)

        if self.sistemas_activos["cab"]:
            comandos_cab = self.cab.procesar_logica_seguridad()
            self._consolidar_comandos(comandos_consolidados, comandos_cab)

        return comandos_consolidados

    def _consolidar_comandos(self, comandos_base: Dict, comandos_nuevos: Dict):
        """Consolidar comandos de diferentes sistemas (lógica OR para seguridad)"""
        # Frenado de emergencia: activar si cualquier sistema lo requiere
        comandos_base["freno_emergencia"] |= comandos_nuevos.get("freno_emergencia", False)

        # Advertencias: activar si cualquier sistema las requiere
        comandos_base["advertencia_sonora"] |= comandos_nuevos.get("advertencia_sonora", False)
        comandos_base["advertencia_visual"] |= comandos_nuevos.get("advertencia_visual", False)

        # Velocidad máxima: tomar el valor más restrictivo
        velocidad_nueva = comandos_nuevos.get("velocidad_maxima", float("inf"))
        if velocidad_nueva < comandos_base["velocidad_maxima"]:
            comandos_base["velocidad_maxima"] = velocidad_nueva

    def actualizar_datos_via(self, datos_via: Dict):
        """
        Actualizar datos de la vía para todos los sistemas

        Args:
            datos_via: Dict con datos de la vía (señales, autoridades, etc.)
        """
        # Procesar datos para ACSES
        if "datos_acses" in datos_via and self.sistemas_activos["acses"]:
            self.acses.recibir_datos_via(datos_via["datos_acses"])

        # Procesar datos para PTC
        if "autoridad_ptc" in datos_via and self.sistemas_activos["ptc"]:
            self.ptc.actualizar_autoridad(datos_via["autoridad_ptc"])

        # Procesar datos para ATC
        if "senal_atc" in datos_via and self.sistemas_activos["atc"]:
            senal = datos_via["senal_atc"]
            self.atc.actualizar_senal(senal["tipo"], senal.get("distancia", float("inf")))

        # Procesar datos para CAB
        if "tren_adelante" in datos_via and self.sistemas_activos["cab"]:
            tren_adelante = datos_via["tren_adelante"]
            self.cab.actualizar_datos_tren_adelante(
                tren_adelante["distancia"], tren_adelante["velocidad"]
            )

    def actualizar_velocidad_tren(self, velocidad: float):
        """Actualizar velocidad del tren en todos los sistemas"""
        if self.sistemas_activos["acses"]:
            self.acses.actualizar_datos_tren(velocidad)

        if self.sistemas_activos["ptc"]:
            self.ptc.actualizar_velocidad(velocidad)

        if self.sistemas_activos["atc"]:
            self.atc.actualizar_velocidad(velocidad)

        if self.sistemas_activos["cab"]:
            self.cab.actualizar_velocidad(velocidad)

    def obtener_estado_completo(self) -> Dict:
        """Obtener estado completo de todos los sistemas"""
        return {
            "region_actual": self.region_actual,
            "sistemas_activos": self.sistemas_activos,
            "acses": (self.acses.obtener_estado() if self.sistemas_activos["acses"] else None),
            "ptc": self.ptc.obtener_estado() if self.sistemas_activos["ptc"] else None,
            "atc": self.atc.obtener_estado() if self.sistemas_activos["atc"] else None,
            "cab": self.cab.obtener_estado() if self.sistemas_activos["cab"] else None,
        }

    def reset_sistemas(self):
        """Reset de todos los sistemas"""
        self.acses.reset()
        self.ptc.reset()
        self.atc.reset()
        self.cab.reset()
        logger.info("Todos los sistemas de señalización norteamericanos reseteados")
