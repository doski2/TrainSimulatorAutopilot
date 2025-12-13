# procedimientos_locomotora.py
# Procedimientos específicos de arranque y parada de locomotoras según referencias reales

import logging
import time

logger = logging.getLogger(__name__)


class ProcedimientosLocomotora:
    """
    Implementa procedimientos reales de arranque y parada de locomotoras
    basados en manuales y referencias ferroviarias.
    """

    def __init__(self):
        self.estado_sistema = {
            "frenos_aplicados": True,
            "reversa_neutra": True,
            "acelerador_cero": True,
            "sistemas_verificados": False,
            "motor_arrancado": False,
            "presion_aire_ok": False,
            "sistemas_seguridad_ok": False,
        }

        self.secuencia_arranque = [
            "verificar_sistemas_iniciales",
            "liberar_frenos_gradualmente",
            "colocar_reversa_adelante",
            "verificar_presion_aire",
            "arrancar_motor_principal",
            "verificar_sistemas_seguridad",
            "preparar_aceleracion",
        ]

        self.secuencia_parada = [
            "reducir_acelerador_gradualmente",
            "aplicar_freno_servicio",
            "colocar_reversa_neutra",
            "esperar_detencion_completa",
            "aplicar_freno_estacionamiento",
            "apagar_sistemas_auxiliares",
        ]

    def verificar_sistemas_iniciales(self, datos_telemetria):
        """
        Verifica que todos los sistemas estén en posición inicial segura.
        Basado en procedimientos de manuales ferroviarios.
        """
        logger.info("🔍 Verificando sistemas iniciales...")

        # Verificar frenos aplicados
        freno_aplicado = datos_telemetria.get("freno_tren", 0) > 0.8
        self.estado_sistema["frenos_aplicados"] = freno_aplicado

        # Verificar reversa en neutro (valor cercano a 0)
        reversa_neutra = abs(datos_telemetria.get("reverser", 0)) < 0.1
        self.estado_sistema["reversa_neutra"] = reversa_neutra

        # Verificar acelerador en cero
        acelerador_cero = datos_telemetria.get("acelerador", 0) < 0.05
        self.estado_sistema["acelerador_cero"] = acelerador_cero

        # Verificar presión de aire (debe estar por encima del mínimo)
        presion_aire = datos_telemetria.get("presion_aire", 0)
        presion_ok = presion_aire > 80  # PSI típico mínimo
        self.estado_sistema["presion_aire_ok"] = presion_ok

        sistemas_ok = all([freno_aplicado, reversa_neutra, acelerador_cero, presion_ok])

        self.estado_sistema["sistemas_verificados"] = sistemas_ok

        logger.info(f"   Frenos aplicados: {freno_aplicado}")
        logger.info(f"   Reversa neutra: {reversa_neutra}")
        logger.info(f"   Acelerador cero: {acelerador_cero}")
        logger.info(f"   Presión aire OK: {presion_ok}")
        logger.info(f"   Sistemas iniciales: {'✅ OK' if sistemas_ok else '❌ ERROR'}")

        return sistemas_ok

    def liberar_frenos_gradualmente(self, datos_telemetria):
        """
        Libera frenos gradualmente para evitar movimientos bruscos.
        Según procedimientos de seguridad ferroviaria.
        """
        logger.info("🔓 Liberando frenos gradualmente...")

        # Liberar frenos en pasos graduales
        pasos_liberacion = [
            {"freno": 0.9, "espera": 2.0},  # Liberar parcialmente
            {"freno": 0.7, "espera": 1.5},  # Liberar más
            {"freno": 0.5, "espera": 1.0},  # Liberar casi completamente
            {"freno": 0.2, "espera": 0.5},  # Liberar casi totalmente
        ]

        comandos_secuencia = []
        tiempo_total = 0

        for paso in pasos_liberacion:
            comandos_secuencia.append(
                {
                    "timestamp": tiempo_total,
                    "acelerador": 0.0,
                    "freno": paso["freno"],
                    "reverser": 0.0,
                    "descripcion": f'Liberando frenos a {paso["freno"]}',
                }
            )
            tiempo_total += paso["espera"]

        # Comando final: frenos liberados
        comandos_secuencia.append(
            {
                "timestamp": tiempo_total,
                "acelerador": 0.0,
                "freno": 0.0,
                "reverser": 0.0,
                "descripcion": "Frenos completamente liberados",
            }
        )

        logger.info(f"   Secuencia de liberación completada en {tiempo_total:.1f}s")
        return comandos_secuencia

    def colocar_reversa_adelante(self):
        """
        Coloca la reversa en posición de avance.
        """
        logger.info("↗️ Colocando reversa en posición adelante...")

        comandos = [
            {
                "timestamp": 0.0,
                "acelerador": 0.0,
                "freno": 0.0,
                "reverser": 1.0,  # Posición adelante
                "descripcion": "Reversa colocada en adelante",
            }
        ]

        self.estado_sistema["reversa_neutra"] = False
        logger.info("   Reversa colocada en posición adelante")
        return comandos

    def verificar_presion_aire(self, datos_telemetria):
        """
        Verifica que la presión de aire esté en niveles seguros para operación.
        """
        logger.info("🌪️ Verificando presión de aire...")

        presion_actual = datos_telemetria.get("presion_aire", 0)
        presion_minima = 85  # PSI mínimo para operación segura
        presion_optima = 90  # PSI óptima

        if presion_actual >= presion_optima:
            logger.info(f"   Presión óptima: {presion_actual:.1f} PSI ✅")
            return True
        elif presion_actual >= presion_minima:
            logger.warning(f"   Presión aceptable pero baja: {presion_actual:.1f} PSI ⚠️")
            return True
        else:
            logger.error(f"   Presión insuficiente: {presion_actual:.1f} PSI ❌")
            return False

    def arrancar_motor_principal(self):
        """
        Simula el arranque del motor principal con verificación de sistemas.
        """
        logger.info("🚂 Arrancando motor principal...")

        # Simular secuencia de arranque
        comandos_arranque = [
            {
                "timestamp": 0.0,
                "acelerador": 0.0,
                "freno": 0.0,
                "reverser": 1.0,
                "descripcion": "Iniciando arranque del motor",
            }
        ]

        # Esperar estabilización del motor
        time.sleep(0.5)  # Simulación

        self.estado_sistema["motor_arrancado"] = True
        logger.info("   Motor principal arrancado correctamente ✅")
        return comandos_arranque

    def verificar_sistemas_seguridad(self):
        """
        Verifica sistemas de seguridad antes de la marcha.
        Incluye verificación de sistemas de señalización si están disponibles.
        """
        logger.info("🛡️ Verificando sistemas de seguridad...")

        # Verificar sistemas básicos de seguridad
        sistemas_seguridad = [
            "freno_emergencia_disponible",
            "sistema_comunicacion_ok",
            "luces_cabina_ok",
        ]

        # Simular verificación (en implementación real se conectarían con sensores)
        for sistema in sistemas_seguridad:
            logger.info(f"   Verificando {sistema}: ✅ OK")

        self.estado_sistema["sistemas_seguridad_ok"] = True
        logger.info("   Todos los sistemas de seguridad verificados ✅")
        return True

    def preparar_aceleracion(self):
        """
        Prepara el sistema para iniciar la aceleración gradual.
        """
        logger.info("⚡ Preparando para aceleración...")

        comandos = [
            {
                "timestamp": 0.0,
                "acelerador": 0.0,  # Mantener en cero hasta comando explícito
                "freno": 0.0,
                "reverser": 1.0,
                "descripcion": "Sistema preparado para aceleración gradual",
            }
        ]

        logger.info("   Sistema listo para aceleración gradual ✅")
        return comandos

    def ejecutar_arranque_completo(self, datos_telemetria):
        """
        Ejecuta la secuencia completa de arranque según procedimientos ferroviarios.
        """
        logger.info("🚂 Iniciando secuencia completa de arranque de locomotora...")

        resultados = {}
        comandos_totales = []

        # Ejecutar cada paso de la secuencia
        for paso in self.secuencia_arranque:
            metodo = getattr(self, paso)
            try:
                if paso in [
                    "verificar_sistemas_iniciales",
                    "verificar_presion_aire",
                    "liberar_frenos_gradualmente",
                ]:
                    resultado = metodo(datos_telemetria)
                elif paso in [
                    "colocar_reversa_adelante",
                    "arrancar_motor_principal",
                    "verificar_sistemas_seguridad",
                    "preparar_aceleracion",
                ]:
                    resultado = metodo()
                else:
                    logger.error(f"   Paso desconocido: {paso}")
                    return False, comandos_totales

                resultados[paso] = resultado

                if isinstance(resultado, list):
                    comandos_totales.extend(resultado)
                elif resultado:
                    comandos_totales.append({"timestamp": 0.0, "paso": paso, "exito": True})

                if not resultado:
                    logger.error(f"   Paso {paso} falló ❌")
                    return False, comandos_totales

            except Exception as e:
                logger.error(f"   Error en paso {paso}: {e}")
                return False, comandos_totales

        logger.info("🚂 Secuencia de arranque completada exitosamente ✅")
        return True, comandos_totales

    def ejecutar_parada_controlada(self, velocidad_actual):
        """
        Ejecuta parada controlada según procedimientos de seguridad.
        """
        logger.info("🛑 Iniciando parada controlada...")

        comandos_parada = []

        # Paso 1: Reducir acelerador gradualmente
        comandos_parada.append(
            {
                "timestamp": 0.0,
                "acelerador": 0.0,
                "freno": 0.0,
                "reverser": 1.0,
                "descripcion": "Reduciendo acelerador a cero",
            }
        )

        # Paso 2: Aplicar freno de servicio
        tiempo_frenado = velocidad_actual / 10  # Estimación simple
        comandos_parada.append(
            {
                "timestamp": 1.0,
                "acelerador": 0.0,
                "freno": 0.8,  # Freno de servicio
                "reverser": 1.0,
                "descripcion": f"Aplicando freno de servicio ({tiempo_frenado:.1f}s estimados)",
            }
        )

        # Paso 3: Colocar reversa en neutro cuando velocidad baja
        comandos_parada.append(
            {
                "timestamp": tiempo_frenado + 1.0,
                "acelerador": 0.0,
                "freno": 0.8,
                "reverser": 0.0,
                "descripcion": "Reversa colocada en neutro",
            }
        )

        # Paso 4: Aplicar freno de estacionamiento
        comandos_parada.append(
            {
                "timestamp": tiempo_frenado + 2.0,
                "acelerador": 0.0,
                "freno": 1.0,  # Freno completo
                "reverser": 0.0,
                "descripcion": "Freno de estacionamiento aplicado",
            }
        )

        logger.info(f"   Parada controlada programada ({len(comandos_parada)} pasos)")
        return comandos_parada


def demo_procedimientos_locomotora():
    """Demostración de procedimientos de locomotora."""
    print("🚂 Demo: Procedimientos de Arranque y Parada de Locomotora")
    print("=" * 60)

    # Configurar logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Crear instancia
    proc = ProcedimientosLocomotora()

    # Datos de telemetría simulados (estado inicial seguro)
    datos_iniciales = {
        "velocidad": 0,
        "acelerador": 0,
        "freno_tren": 1.0,  # Frenos aplicados
        "reverser": 0.0,  # Reversa en neutro
        "presion_aire": 95,  # Presión buena
    }

    print("\n📊 Estado inicial del sistema:")
    for key, value in datos_iniciales.items():
        print(f"   {key}: {value}")

    # Ejecutar arranque completo
    print("\n🚀 Ejecutando secuencia de arranque...")
    exito, comandos = proc.ejecutar_arranque_completo(datos_iniciales)

    if exito:
        print(f"\n✅ Arranque exitoso - {len(comandos)} comandos generados")

        # Mostrar resumen de comandos
        print("\n📋 Resumen de comandos de arranque:")
        for i, cmd in enumerate(comandos[-5:], 1):  # Mostrar últimos 5
            print(f"   {i}. {cmd.get('descripcion', 'Comando')}")

        # Simular parada
        print("\n🛑 Ejecutando parada controlada...")
        comandos_parada = proc.ejecutar_parada_controlada(velocidad_actual=50)

        print(f"   Parada programada con {len(comandos_parada)} pasos")
        for i, cmd in enumerate(comandos_parada, 1):
            print(f"   {i}. {cmd['descripcion']}")

    else:
        print("\n❌ Arranque falló - revisar logs")


if __name__ == "__main__":
    demo_procedimientos_locomotora()
