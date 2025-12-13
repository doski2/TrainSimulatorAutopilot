# input_mapper_integration.py
# Integración directa con archivos InputMapper y KeyMaps

import logging
from pathlib import Path


class InputMapperIntegration:
    def __init__(self, base_path=None):
        if base_path is None:
            base_path = (
                r"C:\Users\doski\Documents\TSClassic Raildriver and Joystick Interface V3.3.0.9"
            )

        self.base_path = Path(base_path)
        self.input_mapper_path = self.base_path / "InputMapper"
        self.key_maps_path = self.base_path / "KeyMaps"
        self.logger = logging.getLogger(__name__)

        # Cache de configuraciones cargadas
        self._input_configs = {}
        self._keymap_configs = {}

    def listar_archivos_input_mapper(self):
        """Lista todos los archivos de configuración InputMapper disponibles."""
        if not self.input_mapper_path.exists():
            self.logger.warning(f"Directorio InputMapper no encontrado: {self.input_mapper_path}")
            return []

        archivos = []
        for archivo in self.input_mapper_path.rglob("*.txt"):
            archivos.append({"ruta": archivo, "nombre": archivo.stem, "tipo": "input_mapper"})

        return archivos

    def listar_archivos_keymaps(self):
        """Lista todos los archivos de configuración KeyMaps disponibles."""
        if not self.key_maps_path.exists():
            self.logger.warning(f"Directorio KeyMaps no encontrado: {self.key_maps_path}")
            return []

        archivos = []
        for archivo in self.key_maps_path.rglob("*.xml"):
            archivos.append({"ruta": archivo, "nombre": archivo.stem, "tipo": "keymap"})

        return archivos

    def parsear_input_mapper(self, archivo_ruta):
        """Parsea un archivo InputMapper (.txt) y extrae configuración de controles."""
        try:
            with open(archivo_ruta, encoding="utf-8") as f:
                contenido = f.read()

            config = {"archivo": str(archivo_ruta), "controles": {}, "metadata": {}}

            # Parsear líneas del archivo InputMapper (formato tabular)
            lineas = contenido.split("\n")

            for linea in lineas:
                linea = linea.strip()
                if not linea or linea.startswith("#") or linea.startswith("CONTROL"):
                    continue

                # Parsear línea CSV: CONTROL, MAIN KEY, EXTRA KEYS, FUNCTION, STATE
                partes = linea.split(",")
                if len(partes) >= 4:
                    control = partes[0].strip()
                    main_key = partes[1].strip()
                    extra_keys = partes[2].strip() if len(partes) > 2 else ""
                    function = partes[3].strip() if len(partes) > 3 else ""
                    state = partes[4].strip() if len(partes) > 4 else ""

                    # Solo procesar controles relevantes para IA
                    controles_ia = [
                        "Regulator",
                        "TrainBrakeControl",
                        "Reverser",
                        "Throttle",
                        "Brake",
                    ]
                    if any(ctrl in control for ctrl in controles_ia):
                        if control not in config["controles"]:
                            config["controles"][control] = {
                                "asignaciones": [],
                                "tipo": "digital",  # Asumir digital por defecto
                            }

                        config["controles"][control]["asignaciones"].append(
                            {
                                "main_key": main_key,
                                "extra_keys": extra_keys,
                                "function": function,
                                "state": state,
                            }
                        )

                        # Determinar si es analógico basado en las funciones
                        if "Start" in function or "Stop" in function:
                            config["controles"][control]["tipo"] = "analogico"

            self._input_configs[str(archivo_ruta)] = config
            return config

        except Exception as e:
            self.logger.error(f"Error parseando InputMapper {archivo_ruta}: {e}")
            return None

    def parsear_keymap(self, archivo_ruta):
        """Parsea un archivo KeyMap (.xml) y extrae configuración de botones."""
        try:
            with open(archivo_ruta, encoding="utf-8") as f:
                contenido = f.read()

            config = {"archivo": str(archivo_ruta), "botones": {}, "metadata": {}}

            # Parsear XML básico (sin librerías externas)
            import re

            # Buscar patrones InputMapper en el XML
            input_mapper_pattern = r"<InputMapper>(.*?)</InputMapper>"
            input_mappers = re.findall(input_mapper_pattern, contenido, re.DOTALL)

            for mapper_content in input_mappers:
                control = ""
                key = ""
                button = ""

                # Extraer control
                control_match = re.search(r"<Control>([^<]*)</Control>", mapper_content)
                if control_match:
                    control = control_match.group(1).strip()

                # Extraer key
                key_match = re.search(r"<Key>([^<]*)</Key>", mapper_content)
                if key_match:
                    key = key_match.group(1).strip()

                # Extraer button (si existe)
                button_match = re.search(r"<Button>([^<]*)</Button>", mapper_content)
                if button_match:
                    button = button_match.group(1).strip()

                # Solo procesar controles relevantes para IA
                if control and (
                    control in ["Regulator", "TrainBrakeControl", "Reverser"]
                    or "Throttle" in control
                    or "Brake" in control
                ):
                    config["botones"][control] = {
                        "key": key,
                        "button": button,
                        "tipo": "digital",
                    }

            self._keymap_configs[str(archivo_ruta)] = config
            return config

        except Exception as e:
            self.logger.error(f"Error parseando KeyMap {archivo_ruta}: {e}")
            return None

    def obtener_configuracion_activa(self, tipo_tren="pasajeros"):
        """Obtiene la configuración activa basada en el tipo de tren."""
        # Buscar archivos relevantes para el tipo de tren
        archivos_input = self.listar_archivos_input_mapper()
        archivos_keymap = self.listar_archivos_keymaps()

        # Filtrar por tipo de tren (lógica básica)
        filtro_tren = tipo_tren.lower()

        input_activo = None
        keymap_activo = None

        # Buscar InputMapper relevante
        for archivo in archivos_input:
            nombre = archivo["nombre"].lower()
            if filtro_tren in nombre or "expert" in nombre:
                input_activo = archivo["ruta"]
                break

        # Si no encuentra específico, usar el primero disponible
        if not input_activo and archivos_input:
            input_activo = archivos_input[0]["ruta"]

        # Buscar KeyMap relevante
        for archivo in archivos_keymap:
            nombre = archivo["nombre"].lower()
            if filtro_tren in nombre or "levers" in nombre.lower():
                keymap_activo = archivo["ruta"]
                break

        # Si no encuentra específico, usar el primero disponible
        if not keymap_activo and archivos_keymap:
            keymap_activo = archivos_keymap[0]["ruta"]

        # Cargar configuraciones
        config_completa = {"tipo_tren": tipo_tren, "input_mapper": None, "keymap": None}

        if input_activo:
            config_completa["input_mapper"] = self.parsear_input_mapper(input_activo)

        if keymap_activo:
            config_completa["keymap"] = self.parsear_keymap(keymap_activo)

        return config_completa

    def validar_configuracion_ia(self, config_ia, config_hardware):
        """Valida que la configuración de IA sea compatible con el hardware disponible."""
        if not config_hardware or not config_hardware.get("input_mapper"):
            return {
                "valido": False,
                "errores": ["No se encontró configuración InputMapper"],
                "advertencias": [],
            }

        errores = []
        advertencias = []

        controles_ia = ["Regulator", "TrainBrakeControl", "Reverser"]
        controles_hardware = config_hardware["input_mapper"].get("controles", {})

        # Verificar que los controles IA tengan asignación hardware
        for control_ia in controles_ia:
            if control_ia not in controles_hardware:
                errores.append(f"Control IA '{control_ia}' no tiene asignación hardware")
            else:
                # Verificar que tenga asignaciones
                asignaciones = controles_hardware[control_ia].get("asignaciones", [])
                if not asignaciones:
                    errores.append(f"Control IA '{control_ia}' no tiene asignaciones de teclas")

        # Verificar configuración de botones si existe
        if config_hardware.get("keymap"):
            botones_hardware = config_hardware["keymap"].get("botones", {})
            for control_ia in controles_ia:
                if control_ia in botones_hardware:
                    boton_config = botones_hardware[control_ia]
                    if not boton_config.get("key"):
                        advertencias.append(
                            f"Botón para '{control_ia}' no tiene asignación de tecla"
                        )

        return {
            "valido": len(errores) == 0,
            "errores": errores,
            "advertencias": advertencias,
        }


def demo_integracion_input_mapper():
    """Demostración de la integración InputMapper/KeyMaps."""
    print("🔧 Integración InputMapper/KeyMaps Demo")
    print("=" * 50)

    integrator = InputMapperIntegration()

    # Listar archivos disponibles
    print("\n📁 Archivos InputMapper encontrados:")
    archivos_input = integrator.listar_archivos_input_mapper()
    for archivo in archivos_input[:5]:  # Mostrar primeros 5
        print(f"  - {archivo['nombre']}")

    print("\n📁 Archivos KeyMaps encontrados:")
    archivos_keymap = integrator.listar_archivos_keymaps()
    for archivo in archivos_keymap[:5]:  # Mostrar primeros 5
        print(f"  - {archivo['nombre']}")

    # Obtener configuración para tren de mercancías
    print("\n🚂 Configuración para tren de mercancías:")
    config_mercancia = integrator.obtener_configuracion_activa("mercancia")

    # Obtener configuración para tren de mercancías
    print("\n🚂 Configuración para tren de mercancías:")
    config_mercancia = integrator.obtener_configuracion_activa("mercancia")

    if config_mercancia["input_mapper"]:
        controles = config_mercancia["input_mapper"]["controles"]
        print(f"  Controles encontrados: {len(controles)}")
        for control, config in controles.items():
            asignaciones = config.get("asignaciones", [])
            print(
                f"    {control}: {len(asignaciones)} asignaciones, tipo: {config.get('tipo', 'unknown')}"
            )
            for _i, asig in enumerate(asignaciones[:2]):  # Mostrar primeras 2 asignaciones
                print(f"      - {asig.get('function', 'N/A')} -> {asig.get('main_key', 'N/A')}")

    if config_mercancia["keymap"]:
        botones = config_mercancia["keymap"]["botones"]
        print(f"  Botones encontrados: {len(botones)}")
        for control, config in botones.items():
            print(
                f"    {control}: key={config.get('key', 'N/A')}, button={config.get('button', 'N/A')}"
            )

    # Validación
    print("\n✅ Validación de configuración:")
    validacion = integrator.validar_configuracion_ia({}, config_mercancia)
    print(f"  Válida: {validacion['valido']}")
    if validacion["errores"]:
        print("  Errores:")
        for error in validacion["errores"]:
            print(f"    - {error}")


if __name__ == "__main__":
    demo_integracion_input_mapper()
