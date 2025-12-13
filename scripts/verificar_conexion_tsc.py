# verificar_conexion_tsc.py
# Script simple para verificar conexión con TSC

import socket


def verificar_conexion():
    """Verifica si TSC está disponible para conexión."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(("localhost", 15678))  # Puerto típico de Raildriver
        sock.close()

        if result == 0:
            print("✅ TSC está conectado y disponible")
            return True
        else:
            print("❌ TSC no está disponible en el puerto esperado")
            return False
    except Exception as e:
        print(f"⚠️ Error al verificar conexión: {e}")
        return False


def instrucciones_detalladas():
    """Muestra instrucciones detalladas para ejecutar TSC."""
    print(
        """
🚂 INSTRUCCIONES PARA EJECUTAR TRAIN SIMULATOR CLASSIC:

PASO 1: Ejecutar Steam
----------
1. Abrir Steam
2. Ir a "Biblioteca"
3. Buscar "Train Simulator Classic" o "RailWorks"
4. Hacer clic en "Jugar"

PASO 2: Configurar TSC
----------
1. Esperar a que cargue el menú principal
2. Seleccionar "Conducir" o "Drive"
3. Elegir una ruta (recomendado: Clinchfield)
4. Seleccionar escenario y hora del día
5. Elegir locomotora (recomendado: EMD SD40)

PASO 3: Ejecutar Raildriver Interface
----------
1. Abrir carpeta: C:\\Users\\doski\\Documents\\TSClassic Raildriver and Joystick Interface V3.3.0.9
2. Ejecutar: TSClassic Interface (x64).exe
3. Verificar que aparezca "Connected to RailWorks" en la ventana

PASO 4: Verificar Conexión
----------
1. Una vez TSC cargado y Raildriver conectado, ejecutar este script
2. Si la conexión es exitosa, proceder con las pruebas reales

⚠️ NOTAS IMPORTANTES:
- TSC debe estar completamente cargado (no en el menú principal)
- El Raildriver debe mostrar "Connected"
- Mantener ambas aplicaciones abiertas durante las pruebas
- Si hay problemas, verificar firewall/antivirus

¿Listo para verificar conexión?
    """
    )


if __name__ == "__main__":
    instrucciones_detalladas()

    input("\nPresiona Enter cuando TSC esté ejecutándose...")

    print("\n🔍 Verificando conexión con TSC...")
    conectado = verificar_conexion()

    if conectado:
        print("\n🎉 ¡Conexión exitosa! Ahora puedes ejecutar las pruebas reales:")
        print("   python test_tsc_real.py")
    else:
        print("\n❌ Conexión fallida. Revisa las instrucciones arriba.")
