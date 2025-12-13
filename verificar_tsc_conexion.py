#!/usr/bin/env python3
"""
verificar_tsc_conexion.py
Script para verificar la conexión con Train Simulator Classic
"""

import os
import time
from datetime import datetime


def verificar_ruta_railworks():
    """Verificar diferentes rutas donde puede estar instalado RailWorks."""
    rutas_posibles = [
        r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks",
        r"C:\Program Files\Steam\steamapps\common\RailWorks",
        r"D:\Steam\steamapps\common\RailWorks",
        r"E:\Steam\steamapps\common\RailWorks",
    ]

    print("🔍 Buscando instalación de Train Simulator Classic...\n")

    ruta_encontrada = None
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            print(f"✅ Encontrado RailWorks en: {ruta}")
            ruta_encontrada = ruta

            # Verificar archivos clave
            railworks_exe = os.path.join(ruta, "RailWorks.exe")
            if os.path.exists(railworks_exe):
                print("   ✅ RailWorks.exe encontrado")
            else:
                print("   ❌ RailWorks.exe NO encontrado")

            # Verificar carpeta de plugins
            plugins_dir = os.path.join(ruta, "plugins")
            if os.path.exists(plugins_dir):
                print("   ✅ Carpeta plugins encontrada")

                # Listar archivos en plugins
                archivos = os.listdir(plugins_dir)
                print(f"   📂 Archivos en plugins ({len(archivos)}):")
                for archivo in archivos[:10]:  # Mostrar solo primeros 10
                    print(f"      - {archivo}")
                if len(archivos) > 10:
                    print(f"      ... y {len(archivos) - 10} más")
            else:
                print("   ❌ Carpeta plugins NO encontrada")

            print()
            break
        else:
            print(f"❌ No encontrado en: {ruta}")

    if not ruta_encontrada:
        print("\n⚠️ No se encontró ninguna instalación de Train Simulator Classic")
        print("Por favor, verifica la ruta de instalación.")
        return None

    return ruta_encontrada


def verificar_raildriver_interface(ruta_railworks):
    """Verificar si el Raildriver Interface está instalado."""
    print("\n🔍 Verificando Raildriver Interface...\n")

    plugins_dir = os.path.join(ruta_railworks, "plugins")

    # Archivos del Raildriver Interface
    archivos_necesarios = ["RailDriver.dll", "PIHid.dll", "PIHidDotNet.dll"]

    todos_encontrados = True
    for archivo in archivos_necesarios:
        ruta_archivo = os.path.join(plugins_dir, archivo)
        if os.path.exists(ruta_archivo):
            print(f"✅ {archivo} encontrado")
        else:
            print(f"❌ {archivo} NO encontrado")
            todos_encontrados = False

    if todos_encontrados:
        print("\n✅ Raildriver Interface parece estar instalado correctamente")
    else:
        print("\n⚠️ Faltan archivos del Raildriver Interface")
        print("Descarga e instala desde: https://www.raildriver.com/")

    return todos_encontrados


def verificar_archivos_telemetria(ruta_railworks):
    """Verificar los archivos de telemetría GetData.txt y SendCommand.txt."""
    print("\n🔍 Verificando archivos de telemetría...\n")

    plugins_dir = os.path.join(ruta_railworks, "plugins")

    getdata_path = os.path.join(plugins_dir, "GetData.txt")
    sendcommand_path = os.path.join(plugins_dir, "SendCommand.txt")

    # Verificar GetData.txt
    if os.path.exists(getdata_path):
        print("✅ GetData.txt encontrado")

        # Leer contenido
        try:
            with open(getdata_path, encoding="utf-8", errors="ignore") as f:
                contenido = f.read().strip()

            if contenido:
                print(f"   📊 Archivo contiene datos ({len(contenido)} caracteres)")

                # Verificar timestamp del archivo
                mtime = os.path.getmtime(getdata_path)
                fecha_modificacion = datetime.fromtimestamp(mtime)
                ahora = datetime.now()
                diferencia = (ahora - fecha_modificacion).total_seconds()

                print(
                    f"   🕐 Última modificación: {fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S')}"
                )

                if diferencia < 5:
                    print(f"   ✅ Archivo actualizado recientemente ({diferencia:.1f}s)")
                    print("   🎮 Train Simulator parece estar ACTIVO")

                    # Mostrar primeras líneas
                    lineas = contenido.split("\n")[:5]
                    print("\n   📄 Primeras líneas del archivo:")
                    for linea in lineas:
                        print(f"      {linea}")
                else:
                    print(f"   ⚠️ Archivo no actualizado en {diferencia:.0f} segundos")
                    print("   💤 Train Simulator NO parece estar activo")
            else:
                print("   ⚠️ Archivo vacío")
                print("   💤 Train Simulator NO está activo")
        except Exception as e:
            print(f"   ❌ Error leyendo archivo: {e}")
    else:
        print("❌ GetData.txt NO encontrado")
        print("   ⚠️ El Raildriver Interface no ha creado el archivo aún")
        print("   💡 Inicia Train Simulator y carga un escenario para generarlo")

    print()

    # Verificar SendCommand.txt
    if os.path.exists(sendcommand_path):
        print("✅ SendCommand.txt encontrado")
    else:
        print("❌ SendCommand.txt NO encontrado")
        print("   💡 Se creará automáticamente al enviar comandos")

    return os.path.exists(getdata_path)


def monitorear_tiempo_real(ruta_railworks, duracion=10):
    """Monitorear el archivo GetData.txt en tiempo real."""
    print(f"\n🔄 Monitoreando GetData.txt durante {duracion} segundos...\n")

    getdata_path = os.path.join(ruta_railworks, "plugins", "GetData.txt")

    if not os.path.exists(getdata_path):
        print("❌ GetData.txt no existe. No se puede monitorear.")
        return

    tiempo_inicio = time.time()
    ultimo_mtime = 0
    contador_actualizaciones = 0

    print("Presiona Ctrl+C para detener el monitoreo antes de tiempo\n")

    try:
        while time.time() - tiempo_inicio < duracion:
            mtime = os.path.getmtime(getdata_path)

            if mtime != ultimo_mtime:
                contador_actualizaciones += 1
                ultimo_mtime = mtime

                # Leer velocidad actual
                try:
                    with open(getdata_path, encoding="utf-8", errors="ignore") as f:
                        contenido = f.read()

                    # Buscar CurrentSpeed
                    for linea in contenido.split("\n"):
                        if "CurrentSpeed" in linea:
                            print(
                                f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Actualización #{contador_actualizaciones} - {linea.strip()}"
                            )
                            break
                except Exception as e:
                    print(f"Error leyendo: {e}")

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n⏹️ Monitoreo detenido por el usuario")

    tiempo_transcurrido = time.time() - tiempo_inicio
    if contador_actualizaciones > 0:
        frecuencia = contador_actualizaciones / tiempo_transcurrido
        print("\n📊 Resumen:")
        print(f"   Actualizaciones detectadas: {contador_actualizaciones}")
        print(f"   Frecuencia: {frecuencia:.2f} actualizaciones/segundo")
        print("   ✅ Train Simulator está ACTIVO y enviando datos")
    else:
        print(f"\n⚠️ No se detectaron actualizaciones en {tiempo_transcurrido:.1f} segundos")
        print("   💤 Train Simulator NO parece estar activo o no hay un escenario cargado")


def main():
    """Función principal."""
    print("=" * 70)
    print("🚂 VERIFICACIÓN DE CONEXIÓN CON TRAIN SIMULATOR CLASSIC")
    print("=" * 70)
    print()

    # 1. Verificar ruta de RailWorks
    ruta_railworks = verificar_ruta_railworks()
    if not ruta_railworks:
        print("\n❌ No se puede continuar sin encontrar la instalación de RailWorks")
        input("\nPresiona Enter para salir...")
        return

    # 2. Verificar Raildriver Interface
    verificar_raildriver_interface(ruta_railworks)

    # 3. Verificar archivos de telemetría
    getdata_existe = verificar_archivos_telemetria(ruta_railworks)

    # 4. Si GetData.txt existe, ofrecer monitoreo en tiempo real
    if getdata_existe:
        print("\n" + "=" * 70)
        respuesta = input("\n¿Quieres monitorear actualizaciones en tiempo real? (s/n): ")
        if respuesta.lower() in ["s", "si", "sí", "y", "yes"]:
            monitorear_tiempo_real(ruta_railworks, duracion=10)

    print("\n" + "=" * 70)
    print("✅ Verificación completada")
    print("=" * 70)

    # Recomendaciones finales
    print("\n📋 RECOMENDACIONES:")
    print("   1. Asegúrate de que Train Simulator Classic esté instalado")
    print("   2. Instala el Raildriver Interface si no lo has hecho")
    print("   3. Inicia Train Simulator y carga un escenario")
    print("   4. Verifica que GetData.txt se actualice constantemente")
    print("   5. Ejecuta este script nuevamente para verificar la conexión")

    input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()
