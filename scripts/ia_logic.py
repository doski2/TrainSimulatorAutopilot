# ia_logic.py
# Módulo de lógica de decisión IA para Train Simulator Autopilot

from concurrent.futures import ThreadPoolExecutor

import pandas as pd


def decidir_accion(
    datos_telemetria,
    velocidad_objetivo=80,
    limite_frenado=10,
    pendiente=0,
    tipo_tren="pasajeros",
):
    """
    Lógica avanzada de IA: ajustar acelerador y freno basado en velocidad actual, objetivo, pendiente, distancia y tipo de tren.

    Args:
        datos_telemetria (dict): Datos procesados de telemetría.
        velocidad_objetivo (float): Velocidad deseada en km/h.
        limite_frenado (float): Distancia mínima para frenar (km).
        pendiente (float): Pendiente actual (‰, positivo = subida).
        tipo_tren (str): Tipo de tren ('mercancia' o 'pasajeros').

    Returns:
        dict: Comandos para el simulador (acelerador, freno, ajustes).
    """
    velocidad_actual = datos_telemetria.get("velocidad", 0)
    distancia_a_parada = datos_telemetria.get(
        "distancia_parada", float("inf")
    )  # Distancia a próxima parada

    # Lógica adaptativa según tipo de tren
    if tipo_tren.lower() == "mercancia":
        # Trenes de mercancías: más conservadores, frenado más suave pero anticipado
        sensibilidad_freno = 0.7
        velocidad_maxima = 80
        factor_aceleracion = 0.8  # Aceleración más gradual
        ajuste_frenado_anticipado = 1.2  # Más distancia de frenado
    elif tipo_tren.lower() == "pasajeros":
        # Trenes de pasajeros: más responsivos, frenado más agresivo
        sensibilidad_freno = 0.9
        velocidad_maxima = 120
        factor_aceleracion = 1.0  # Aceleración normal
        ajuste_frenado_anticipado = 1.0  # Frenado normal
    else:
        # Valores por defecto
        sensibilidad_freno = 0.8
        velocidad_maxima = 100
        factor_aceleracion = 0.9
        ajuste_frenado_anticipado = 1.0

    # Ajustar velocidad objetivo según límites del tipo de tren
    velocidad_objetivo = min(velocidad_objetivo, velocidad_maxima)

    # Ajuste por pendiente: en subida reducir aceleración, en bajada aumentar precaución
    ajuste_pendiente = pendiente * 0.01  # Ajuste simple

    # Límite de frenado ajustado según tipo de tren
    limite_frenado_ajustado = limite_frenado * ajuste_frenado_anticipado

    # Lógica de frenado anticipado
    if distancia_a_parada < limite_frenado_ajustado:
        # Frenar si cerca de parada
        acelerador = 0.0
        freno = min(1.0, (velocidad_actual / distancia_a_parada) * 0.5 * sensibilidad_freno)
    elif velocidad_actual < (velocidad_objetivo - 5 - ajuste_pendiente):
        acelerador = min(1.0, (velocidad_objetivo - velocidad_actual) / 50 * factor_aceleracion)
        freno = 0.0
    elif velocidad_actual > (velocidad_objetivo + 5 + ajuste_pendiente):
        acelerador = 0.0
        freno = min(1.0, (velocidad_actual - velocidad_objetivo) / 50 * sensibilidad_freno)
    else:
        acelerador = 0.5 * factor_aceleracion
        freno = 0.0

    return {
        "acelerador": acelerador,
        "freno": freno,
        "velocidad_objetivo": velocidad_objetivo,
        "ajuste_pendiente": ajuste_pendiente,
        "tipo_tren": tipo_tren,
        "sensibilidad_freno": sensibilidad_freno,
        "velocidad_maxima": velocidad_maxima,
    }


class IAConduccionOptimizada:
    def __init__(self, tipo_tren="pasajeros"):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.frecuencia_actualizacion = 0.1  # 100ms por defecto
        self.tipo_tren = tipo_tren  # Tipo de tren para lógica adaptativa

    def decidir_accion_paralela(
        self, datos_telemetria, objetivo_velocidad, limite_velocidad, pendiente
    ):
        """
        Versión optimizada con procesamiento paralelo para múltiples escenarios.
        """
        # Procesar decisión principal
        decision_principal = decidir_accion(
            datos_telemetria,
            objetivo_velocidad,
            limite_velocidad,
            pendiente,
            self.tipo_tren,
        )

        # Procesar escenarios alternativos en paralelo
        escenarios = [
            (
                datos_telemetria.copy(),
                objetivo_velocidad + 5,
                limite_velocidad,
                pendiente,
                self.tipo_tren,
            ),
            (
                datos_telemetria.copy(),
                objetivo_velocidad - 5,
                limite_velocidad,
                pendiente,
                self.tipo_tren,
            ),
        ]

        futuros = [self.executor.submit(decidir_accion, *esc) for esc in escenarios]
        decisiones_alternativas = [f.result() for f in futuros]

        return {
            "decision_principal": decision_principal,
            "decisiones_alternativas": decisiones_alternativas,
        }

    def ajustar_frecuencia(self, carga_sistema):
        """
        Ajusta frecuencia de actualización basada en carga del sistema.
        """
        if carga_sistema > 80:
            self.frecuencia_actualizacion = 0.2  # Reducir frecuencia en alta carga
        elif carga_sistema < 30:
            self.frecuencia_actualizacion = 0.05  # Aumentar frecuencia en baja carga
        else:
            self.frecuencia_actualizacion = 0.1

        return self.frecuencia_actualizacion


# Instancia global para uso optimizado
ia_optimizada = IAConduccionOptimizada()


def generar_comandos(comandos_ia):
    """
    Genera comandos en formato para enviar al simulador.
    """
    return f"SET_THROTTLE {comandos_ia['acelerador']}; SET_BRAKE {comandos_ia['freno']}"


# Ejemplo de uso
if __name__ == "__main__":
    # Simular datos de telemetría
    datos = {
        "velocidad": 70,
        "acelerador": 0.5,
        "freno": 0.1,
        "presion": 120,
        "fecha_hora": pd.Timestamp.now().isoformat(),
    }

    comandos = decidir_accion(datos)
    comando_str = generar_comandos(comandos)
    print("Comandos generados:", comando_str)
