from tsc_integration import TSCIntegration

tsc = TSCIntegration()
tsc.ruta_archivo = r"C:\Users\doski\TrainSimulatorAutopilot\GetData.txt"

# Leer el archivo manualmente para debug
with open(tsc.ruta_archivo, encoding="utf-8") as f:
    lineas = f.readlines()

print("Líneas leídas:")
for i, linea in enumerate(lineas):
    print(f'{i}: "{linea.strip()}"')

print()
print("Procesando...")
datos = {}
i = 0
while i < len(lineas):
    linea = lineas[i].strip()
    print(f'Procesando línea {i}: "{linea}"')
    if linea.startswith("ControlName:"):
        nombre_control = linea.split(":", 1)[1].strip()
        print(f'  Nombre control: "{nombre_control}"')
        # Buscar el valor correspondiente
        j = i + 1
        while j < len(lineas) and not lineas[j].strip().startswith("ControlValue:"):
            j += 1

        if j < len(lineas):
            valor_str = lineas[j].strip().split(":", 1)[1].strip()
            print(f'  Valor string: "{valor_str}"')
            try:
                valor = float(valor_str)
                datos[nombre_control] = valor
                print(f"  Guardado: {nombre_control} = {valor}")
            except ValueError:
                datos[nombre_control] = valor_str
                print(f"  Guardado como string: {nombre_control} = {valor_str}")

    i += 1

print()
print("Datos finales:")
for key, value in datos.items():
    print(f"{key}: {value}")

print()
print("Probando conversión...")
converted_data = tsc.convertir_datos_ia(datos)
print("Datos convertidos:")
for key, value in converted_data.items():
    if (
        value != 0.0 and value != 1 and value != 90.0 and value != 1000.0 and value != 400.0
    ):  # Solo mostrar valores no default
        print(f"{key}: {value}")
