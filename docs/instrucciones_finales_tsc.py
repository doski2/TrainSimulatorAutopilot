# instrucciones_finales_tsc.py
# Instrucciones finales para completar la integración TSC

import socket
import subprocess
import sys

print(
    """
🚂 INSTRUCCIONES FINALES PARA COMPLETAR LA INTEGRACIÓN

TSC está ejecutándose pero necesita configuración específica:

PASOS PARA CONFIGURAR TSC CORRECTAMENTE:
=========================================

1. **En TSC (RailWorks), navega al menú principal:**
   - Si estás en el menú de Steam, selecciona "Jugar"
   - Deberías ver el menú principal de TSC

2. **Selecciona "Drive" (Conducir):**
   - NO selecciones "Quick Drive"
   - Selecciona "Drive" para escenarios completos

3. **Elige escenario:**
   - Ruta: Clinchfield (DTG)
   - Duración: Cualquier (ej: 2 horas)
   - Hora del día: Cualquier (ej: Día)
   - Clima: Cualquier

4. **Selecciona locomotora:**
   - Busca: EMD SD40
   - Elige: [CLF] EMD SD40 Grey ND
   - Confirma selección

5. **Espera a que cargue el escenario:**
   - Verás la carga del escenario
   - Aparecerá la cabina de la locomotora
   - TSC estará listo cuando puedas controlar el tren

6. **Verifica Raildriver:**
   - La ventana del Raildriver debería mostrar "Connected to RailWorks"
   - Si no, reinicia el Raildriver interface

7. **Ejecuta las pruebas:**
   - Una vez en la cabina, ejecuta: python test_tsc_real.py
   - La IA tomará control automáticamente

⚠️ NOTAS CRÍTICAS:
- TSC debe estar en la cabina del tren (no en menú)
- Raildriver debe mostrar "Connected"
- Mantén TSC como ventana activa durante las pruebas
- Si hay problemas, verifica firewall/antivirus

¿ESCENARIO CONFIGURADO? Ejecuta: python test_tsc_real.py
"""
)

# Verificar estado actual
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(("localhost", 15678))
    sock.close()

    if result == 0:
        print("✅ ¡CONEXIÓN ESTABLE! TSC está listo para pruebas")
        print("Ejecutando pruebas automáticamente...")
        subprocess.run([sys.executable, "test_tsc_real.py"], input="s\n", text=True)
    else:
        print("❌ TSC ejecutándose pero no conectado aún")
        print("Sigue las instrucciones arriba para configurar el escenario")

except Exception as e:
    print(f"❌ Error verificando conexión: {e}")
    print("Asegúrate de que TSC esté ejecutándose")
