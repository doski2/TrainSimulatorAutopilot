#!/usr/bin/env python3
"""
autopilot_system.py
Sistema completo de piloto automático para Train Simulator Classic
Integra TSC + IA + Control de comandos
"""

import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

from autopilot.traction_control import TractionConfig, TractionControl  # noqa: E402
from tsc_integration import TSCIntegration

logger = logging.getLogger(__name__)


class IASistema:
    """Sistema de Inteligencia Artificial para control de tren."""

    def __init__(self):
        """Inicializar el sistema IA."""
        self.historial_decisiones = []
        self.umbral_cambio_velocidad = 0.5  # mph
        self.umbral_aceleracion_maxima = 0.8
        self.umbral_freno_maximo = 0.9

        # Métricas de IA
        self.metrics = {
            "decision_total": 0,
            "decision_total_time_ms": 0.0,
            "decision_last_latency_ms": 0.0,
        }

    def procesar_telemetria(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesar datos de telemetría y generar comandos de control.

        Args:
            datos: Datos de telemetría del tren

        Returns:
            Diccionario con comandos de control
        """
        # Prefer keys produced by TSCIntegration (km/h) but keep backwards compatibility
        velocidad_actual = datos.get("velocidad_actual") if datos.get("velocidad_actual") is not None else datos.get("velocidad", 0)
        limite_velocidad = datos.get("limite_velocidad") if datos.get("limite_velocidad") is not None else datos.get("limite_velocidad_actual", 80)
        pendiente = datos.get("pendiente", 0)
        aceleracion = datos.get("aceleracion", 0)
        distancia_parada = datos.get("distancia_parada", 1000)

        # Lógica de decisión principal
        comandos = {
            "timestamp": datetime.now().isoformat(),
            "velocidad_actual": velocidad_actual,
            "limite_velocidad": limite_velocidad,
            "decision": "",
            "acelerador": 0.0,
            "freno_tren": 0.0,
            "freno_motor": 0.0,
            "freno_dinamico": 0.0,
            "reverser": datos.get("reverser", 1),
            "razon_decision": "",
        }

        # Decisión basada en velocidad vs límite
        if velocidad_actual > limite_velocidad * 1.05:
            # Exceso de velocidad - frenar
            comandos["decision"] = "REDUCIR_VELOCIDAD"
            exceso = velocidad_actual - limite_velocidad
            intensidad_freno = min(self.umbral_freno_maximo, exceso / 10)
            comandos["freno_tren"] = round(intensidad_freno, 3)
            comandos["razon_decision"] = (
                f"Velocidad {velocidad_actual:.1f} > límite {limite_velocidad:.1f}"
            )

        elif velocidad_actual < limite_velocidad * 0.95:
            # Muy por debajo del límite - acelerar
            comandos["decision"] = "ACELERAR"
            deficit = limite_velocidad - velocidad_actual
            intensidad_acelerador = min(self.umbral_aceleracion_maxima, deficit / 20)
            comandos["acelerador"] = round(intensidad_acelerador, 3)
            comandos["razon_decision"] = (
                f"Velocidad {velocidad_actual:.1f} < límite {limite_velocidad:.1f}"
            )
            # Log con más detalle para depuración de por qué IA eligió esta aceleración
            logger.info(
                "[IA] ACELERANDO - velocidad_actual=%.2f, limite=%.2f, deficit=%.2f, acelerador=%.3f",
                velocidad_actual,
                limite_velocidad,
                deficit,
                comandos["acelerador"],
            )
            # Mantener una impresión legible para consola durante pruebas interactivas
            print(
                f"[IA] ACELERANDO - Vel: {velocidad_actual:.1f}, Limite: {limite_velocidad:.1f}, Acelerador: {comandos['acelerador']:.3f}"
            )

        else:
            # Velocidad adecuada - mantener
            comandos["decision"] = "MANTENER_VELOCIDAD"
            comandos["razon_decision"] = (
                f"Velocidad adecuada: {velocidad_actual:.1f} ≈ {limite_velocidad:.1f}"
            )

        # Ajustes por pendiente
        if abs(pendiente) > 1:
            if pendiente > 0:  # Subida
                comandos["decision"] += "_SUBIDA"
                comandos["acelerador"] *= 1.3  # Más acelerador en subidas
                comandos["razon_decision"] += f" (compensando subida {pendiente:.1f}‰)"
            else:  # Bajada
                comandos["decision"] += "_BAJADA"
                comandos["freno_tren"] *= 0.7  # Menos freno en bajadas
                comandos["razon_decision"] += f" (aprovechando bajada {pendiente:.1f}‰)"

        # Ajustes por aceleración actual
        if abs(aceleracion) > 0.1:
            if aceleracion > 0 and comandos["acelerador"] > 0:
                # Ya acelerando, reducir para evitar overshoot
                comandos["acelerador"] *= 0.8
                comandos["razon_decision"] += f" (controlando aceleración {aceleracion:.3f})"
            elif aceleracion < -0.1 and comandos["freno_tren"] > 0:
                # Ya frenando fuerte, reducir intensidad
                comandos["freno_tren"] *= 0.9
                comandos["razon_decision"] += f" (controlando deceleración {aceleracion:.3f})"

        # Ajustes por distancia de parada
        if distancia_parada < 500 and velocidad_actual > 5:
            comandos["decision"] = "APROXIMANDO_PARADA"
            comandos["freno_tren"] = min(0.5, comandos["freno_tren"] + 0.2)
            comandos["acelerador"] = 0.0
            comandos["razon_decision"] = f"Preparando parada a {distancia_parada:.0f}m"

        # Redondear valores finales
        comandos["acelerador"] = round(comandos["acelerador"], 3)
        comandos["freno_tren"] = round(comandos["freno_tren"], 3)

        # Registrar decisión en historial
        self.historial_decisiones.append(
            {
                "timestamp": comandos["timestamp"],
                "decision": comandos["decision"],
                "velocidad": velocidad_actual,
                "limite": limite_velocidad,
                "comandos": comandos.copy(),
            }
        )

        # Mantener solo últimas 100 decisiones
        if len(self.historial_decisiones) > 100:
            self.historial_decisiones.pop(0)

        return comandos

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del rendimiento del sistema IA."""
        if not self.historial_decisiones:
            return {"total_decisiones": 0}

        decisiones_por_tipo = {}
        for decision in self.historial_decisiones:
            tipo = decision["decision"].split("_")[0]
            decisiones_por_tipo[tipo] = decisiones_por_tipo.get(tipo, 0) + 1

        return {
            "total_decisiones": len(self.historial_decisiones),
            "decisiones_por_tipo": decisiones_por_tipo,
            "ultima_decision": (
                self.historial_decisiones[-1]["decision"] if self.historial_decisiones else None
            ),
            "tiempo_ultima_decision": (
                self.historial_decisiones[-1]["timestamp"] if self.historial_decisiones else None
            ),
        }


class AutopilotSystem:
    """Sistema completo de piloto automático."""

    def __init__(self):
        """Inicializar el sistema de piloto automático."""
        self.tsc = TSCIntegration()
        self.ia = IASistema()
        self.modo_automatico = False
        self.timestamp_inicio = None
        self.sesion_activa = False
        # Configurable behavior: whether autopilot applies brakes based on signals
        self.autobrake_by_signal = True
        # Traction control helper for slip detection and throttle mitigation
        self.traction = TractionControl(TractionConfig())
        # Timestamp of last traction update to compute dt
        self._last_traction_ts = None
        # Traction metrics
        self.ia.metrics.setdefault("traction_slip_total", 0)
        self.ia.metrics.setdefault("traction_commands_sent_total", 0)

        # AI accelerator send control (cooldown and thresholds)
        self._last_ai_accel_sent_ts = 0.0
        self._last_ai_accel_sent_value: float | None = None
        self._ai_accel_cooldown = float(os.getenv("AI_ACCEL_COOLDOWN", "1.0"))
        self._ai_accel_min_diff = float(os.getenv("AI_ACCEL_MIN_DIFF", "0.05"))

    def iniciar_sesion(self) -> bool:
        """
        Iniciar sesión de piloto automático.

        Returns:
            True si se inició correctamente
        """
        if not self.tsc.archivo_existe():
            print("ERROR: No se puede iniciar: archivo GetData.txt no encontrado")
            return False

        self.modo_automatico = False
        self.timestamp_inicio = datetime.now()
        self.sesion_activa = True

        print("[TREN] Sesion de piloto automatico iniciada")
        print(f"[HORA] {self.timestamp_inicio.strftime('%Y-%m-%d %H:%M:%S')}")
        return True

    def finalizar_sesion(self):
        """Finalizar sesión de piloto automático."""
        # Detener modo automático y hilo
        if self.modo_automatico:
            self.desactivar_modo_automatico()

        self.modo_automatico = False
        self.sesion_activa = False

        estadisticas = self.ia.obtener_estadisticas()
        print("\n[ESTADISTICAS] SESION FINALIZADA")
        print(
            f"[DURACION] Duracion: {datetime.now() - self.timestamp_inicio if self.timestamp_inicio else 'N/A'}"
        )
        print(f"[IA] Decisiones IA: {estadisticas.get('total_decisiones', 0)}")
        print(f"[TIPOS] Tipos: {estadisticas.get('decisiones_por_tipo', {})}")

    def activar_modo_automatico(self) -> bool:
        """
        Activar modo automático (IA controla el tren).

        Returns:
            True si se activó correctamente
        """
        if not self.sesion_activa:
            print("ERROR: Sesion no iniciada")
            return False

        self.modo_automatico = True
        print("[IA] MODO AUTOMATICO ACTIVADO - IA controlando el tren")

        # Enviar comando al Lua para activar autopiloto
        self.tsc.enviar_comandos({"autopilot": True})

        # NO iniciar hilo de control automático - el Lua lo maneja internamente
        # El control detallado ahora se hace en el script Lua

        return True

    def desactivar_modo_automatico(self):
        """Desactivar modo automático."""
        self.modo_automatico = False
        print("[MANUAL] MODO AUTOMATICO DESACTIVADO - Control manual")

        # Enviar comando al Lua para desactivar autopiloto
        self.tsc.enviar_comandos({"autopilot": False})

        # NO detener hilo de control automático - nunca se inició

    def ejecutar_ciclo_control(self) -> Optional[Dict[str, Any]]:
        """
        Ejecutar un ciclo completo de control.

        Returns:
            Resultado del ciclo o None si no hay datos nuevos
        """
        if not self.sesion_activa:
            return None

        # Obtener datos de telemetría
        datos_telemetria = self.tsc.obtener_datos_telemetria()

        if not datos_telemetria:
            return None

        # Procesar con IA y medir latencia
        start = time.time()
        comandos = self.ia.procesar_telemetria(datos_telemetria)
        elapsed_ms = (time.time() - start) * 1000.0
        # Update IA metrics
        try:
            # Ensure metrics storage is a dict; if it's None or a wrong type, initialize
            if not isinstance(self.ia.metrics, dict):
                logger.warning("IA metrics container missing or invalid (%r); initializing to empty dict", self.ia.metrics)
                self.ia.metrics = {}

            self.ia.metrics["decision_last_latency_ms"] = round(elapsed_ms, 3)
            # Increment counters defensively; initialize if missing
            self.ia.metrics["decision_total"] = int(self.ia.metrics.get("decision_total", 0)) + 1
            self.ia.metrics["decision_total_time_ms"] = float(self.ia.metrics.get("decision_total_time_ms", 0.0)) + elapsed_ms
        except Exception as e:
            # Log the exception so we can debug issues with metrics storage without
            # interrupting the control loop (metrics must be non-fatal)
            logger.exception("Failed to update IA metrics after decision: %s", e)

        # Reglas de seguridad por señal - overrides (solo si autobrake_by_signal está activado)
        try:
            aspecto = datos_telemetria.get("senal_procesada")
            # Si el ajuste está desactivado, ignorar las reglas de señal
            if not self.autobrake_by_signal:
                aspecto = None
            if aspecto is not None:
                # Stop (ROJA): aplicar freno máximo
                if aspecto == self.tsc.SIGNAL_STOP:
                    comandos["decision"] = "SEÑAL_ROJA_STOP"
                    comandos["freno_tren"] = max(comandos.get("freno_tren", 0.0), 1.0)
                    comandos["acelerador"] = 0.0
                # Caution (AMARILLA): reducir velocidad si es necesario
                elif aspecto == self.tsc.SIGNAL_CAUTION:
                    comandos["decision"] = "SEÑAL_AMARILLA"
                    # Aplicar freno leve si está y añadir motivo
                    comandos["freno_tren"] = max(comandos.get("freno_tren", 0.0), 0.2)
                    comandos["acelerador"] = min(comandos.get("acelerador", 0.0), 0.0)
        except Exception:
            pass

        # Enviar comandos ACCELERAR desde IA cuando corresponda (modo automático)
        try:
            if self.modo_automatico and comandos.get("decision") == "ACELERAR":
                desired = float(comandos.get("acelerador", 0.0))
                now = time.time()
                # Determine baseline for comparison
                baseline = self._last_ai_accel_sent_value
                if baseline is None:
                    baseline = float(datos_telemetria.get("acelerador", 0.0))
                if (now - self._last_ai_accel_sent_ts) >= self._ai_accel_cooldown and abs(desired - baseline) >= self._ai_accel_min_diff:
                    # Compute snapped notch for logging visibility
                    try:
                        snapped = self.tsc._snap_to_notch(desired)
                    except Exception:
                        snapped = desired
                    logger.info("[IA] Computed acelerador desired=%.3f snapped=%.3f (baseline=%.3f)", desired, snapped, baseline)
                    ok = self.tsc.enviar_comandos({"acelerador": desired})
                    if ok:
                        self._last_ai_accel_sent_ts = now
                        self._last_ai_accel_sent_value = snapped
        except Exception as e:
            logger.exception("Failed to send IA accelerator command: %s", e)

        # Detección de patinaje y mitigación (si tenemos telemetría relevante)
        try:
            now = time.time()
            if self._last_traction_ts is None:
                dt = 0.1
            else:
                dt = max(1e-6, now - self._last_traction_ts)
            self._last_traction_ts = now

            # Preferir intensidad normalizada si está disponible
            slip_int = datos_telemetria.get("deslizamiento_ruedas_intensidad")
            # Velocidad IA está en km/h; convertir a m/s para compatibilidad
            vel_kmh = datos_telemetria.get("velocidad_actual", 0.0)
            speed_m_s = float(vel_kmh) / 3.6 if vel_kmh is not None else None
            rpm = datos_telemetria.get("rpm", 0.0)
            amperaje = datos_telemetria.get("amperaje", 0.0)

            slip_detected = self.traction.detect_slip(
                speed_m_s if speed_m_s is not None else None,
                None,
                dt,
                slip_intensity=slip_int,
            )

            if slip_detected:
                # Increment metric
                try:
                    self.ia.metrics["traction_slip_total"] = int(self.ia.metrics.get("traction_slip_total", 0)) + 1
                except Exception:
                    self.ia.metrics["traction_slip_total"] = 1

                # Si estamos en modo automático, enviar ajuste de throttle inmediato
                if self.modo_automatico:
                    current_th = float(datos_telemetria.get("acelerador", 0.0))
                    new_th = self.traction.compute_throttle_adjustment(current_th, True)
                    # Enviar comando de throttle (la integración mapeará a Regulator/VirtualThrottle)
                    ok = self.tsc.enviar_comandos({"acelerador": new_th})
                    if ok:
                        try:
                            self.ia.metrics["traction_commands_sent_total"] = int(self.ia.metrics.get("traction_commands_sent_total", 0)) + 1
                        except Exception:
                            self.ia.metrics["traction_commands_sent_total"] = 1
                        logger.info("Applied traction mitigation: throttle %.3f -> %.3f", current_th, new_th)
        except Exception as e:
            logger.exception("Error during traction detection/mitigation: %s", e)

        # Enviar comandos si está en modo automático
        if self.modo_automatico:
            # Solo enviar comandos de alto nivel al Lua, no comandos detallados
            # El Lua maneja el control interno basado en la telemetría
            pass

        return {
            "telemetria": datos_telemetria,
            "comandos": comandos,
            "modo_automatico": self.modo_automatico,
        }

    def mostrar_estado(self):
        """Mostrar estado actual del sistema."""
        estado_tsc = self.tsc.estado_conexion()
        estadisticas_ia = self.ia.obtener_estadisticas()

        print("\n[ESTADO] ESTADO DEL SISTEMA:")
        print(f"   Sesión activa: {self.sesion_activa}")
        print(f"   Modo automático: {self.modo_automatico}")
        print(f"   Archivo TSC: {estado_tsc['archivo_existe']}")
        print(f"   Datos disponibles: {estado_tsc['datos_disponibles']}")
        print(f"   Controles leídos: {estado_tsc['controles_leidos']}")
        print(f"   Decisiones IA: {estadisticas_ia.get('total_decisiones', 0)}")

    def start(self):
        """Iniciar el piloto automático (método para integración web)."""
        if not self.sesion_activa:
            if not self.iniciar_sesion():
                raise Exception("No se pudo iniciar la sesión del piloto automático")
        if not self.modo_automatico:
            if not self.activar_modo_automatico():
                raise Exception("No se pudo activar el modo automático")

    def stop(self):
        """Detener el piloto automático (método para integración web)."""
        if self.modo_automatico:
            self.desactivar_modo_automatico()
        if self.sesion_activa:
            self.finalizar_sesion()

    def modo_prueba_interactivo(self):
        """Modo de prueba interactivo."""
        print("[TREN] MODO PRUEBA INTERACTIVO")
        print("Comandos disponibles:")
        print("  'start' - Iniciar sesión")
        print("  'auto' - Activar modo automático")
        print("  'manual' - Desactivar modo automático")
        print("  'status' - Mostrar estado")
        print("  'test' - Ejecutar ciclo de prueba")
        print("  'quit' - Salir")

        while True:
            try:
                comando = input("\n[COMANDO] Comando: ").strip().lower()

                if comando == "quit":
                    break
                elif comando == "start":
                    if self.iniciar_sesion():
                        print("[OK] Sesion iniciada")
                    else:
                        print("[ERROR] Error al iniciar sesion")
                elif comando == "auto":
                    if self.activar_modo_automatico():
                        print("[OK] Modo automatico activado")
                    else:
                        print("[ERROR] Error al activar modo automatico")
                elif comando == "manual":
                    self.desactivar_modo_automatico()
                elif comando == "status":
                    self.mostrar_estado()
                elif comando == "test":
                    resultado = self.ejecutar_ciclo_control()
                    if resultado:
                        print("[OK] Ciclo ejecutado:")
                        print(
                            f"   Velocidad: {resultado['telemetria'].get('velocidad', 0):.1f} mph"
                        )
                        print(f"   Decision: {resultado['comandos']['decision']}")
                        print(f"   Acelerador: {resultado['comandos']['acelerador']}")
                        print(f"   Freno: {resultado['comandos']['freno_tren']}")
                    else:
                        print("[ERROR] No hay datos nuevos")
                else:
                    print("[?] Comando no reconocido")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] Error: {e}")

        self.finalizar_sesion()


def main():
    """Función principal."""
    print("[TREN] TRAIN SIMULATOR AUTOPILOT SYSTEM")
    print("=" * 50)

    system = AutopilotSystem()
    system.modo_prueba_interactivo()

    print("\n[Hasta luego!]")


if __name__ == "__main__":
    main()
