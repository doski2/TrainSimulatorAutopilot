# sincronizacion_telemetria.py
# Script para optimizar frecuencia de actualización y sincronización de telemetría

import threading
import time

import psutil


class SincronizadorTelemetria:
    def __init__(self, frecuencia_base=0.1):
        self.frecuencia_base = frecuencia_base  # 100ms
        self.frecuencia_actual = frecuencia_base
        self.ultima_actualizacion = time.time()
        self.datos_cache = {}
        self.lock = threading.Lock()

    def ajustar_frecuencia_dinamica(self):
        """
        Ajusta frecuencia basada en carga del sistema y rendimiento.
        """
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memoria_percent = psutil.virtual_memory().percent

        # Lógica de ajuste
        if cpu_percent > 80 or memoria_percent > 85:
            self.frecuencia_actual = self.frecuencia_base * 2  # Reducir frecuencia
        elif cpu_percent < 30 and memoria_percent < 50:
            self.frecuencia_actual = self.frecuencia_base * 0.5  # Aumentar frecuencia
        else:
            self.frecuencia_actual = self.frecuencia_base

        return self.frecuencia_actual

    def sincronizar_datos(self, nuevos_datos):
        """
        Sincroniza datos con frecuencia optimizada.
        """
        ahora = time.time()

        with self.lock:
            if ahora - self.ultima_actualizacion >= self.frecuencia_actual:
                self.datos_cache.update(nuevos_datos)
                self.ultima_actualizacion = ahora
                return True  # Datos actualizados
            else:
                return False  # No actualizar aún

    def obtener_datos_sincronizados(self):
        """
        Obtiene datos actuales con sincronización.
        """
        with self.lock:
            return self.datos_cache.copy()


def simular_sincronizacion():
    """
    Simula sincronización de telemetría con ajuste dinámico.
    """
    sincronizador = SincronizadorTelemetria()

    print("Iniciando simulación de sincronización...")

    for i in range(50):
        # Ajustar frecuencia
        freq = sincronizador.ajustar_frecuencia_dinamica()

        # Simular nuevos datos
        nuevos_datos = {"velocidad": 70 + (i % 20), "timestamp": time.time()}

        # Intentar sincronizar
        actualizado = sincronizador.sincronizar_datos(nuevos_datos)

        if actualizado:
            print(f"Iteración {i}: Datos actualizados - Frecuencia: {freq:.3f}s")
        else:
            print(f"Iteración {i}: Esperando sincronización")

        time.sleep(0.05)  # Simular intervalo

    print("Simulación completada.")
    print(f"Frecuencia final: {sincronizador.frecuencia_actual:.3f}s")


if __name__ == "__main__":
    simular_sincronizacion()
