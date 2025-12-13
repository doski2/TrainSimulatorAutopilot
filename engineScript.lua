-- setup lighting environment
--
-- fogParams ( enabled, start distance, end distance, r, g, b )
--
-- bloomEnable ( enabled )
--
-- setFov ( fovDeg )
--
-- setDof ( nearPlane, focalPoint, farPlane )
--
-- logTrainData ( filePath )
--   Registra variables internas del tren en un archivo para análisis IA.
--   Ejemplo de uso: logTrainData("C:/Users/doski/TrainSimulatorAutopilot/data/raw/train_log.txt")
-- This function is automatically run if the game is a debug build
function autorunDEBUG()
	setFov(65)
	setDof(0, 4000)
end

-- This function is automatically run if the game is a release build
function autorun()
	setFov(65)
	setDof(0, 4000)
end

-- Función opcional para registrar datos del tren
-- Puedes personalizar las variables a registrar según tus necesidades
function logTrainData(filePath)
	local speed = GetControlValue("SpeedometerKPH", 0)
	local position = GetControlValue("Position", 0)
	local throttle = GetControlValue("Throttle", 0)
	local brake = GetControlValue("Brake", 0)
	local logLine = string.format("Velocidad: %s km/h | Posición: %s | Throttle: %s | Freno: %s\n", speed, position, throttle, brake)
	local file = io.open(filePath, "a")
	if file then
		file:write(logLine)
		file:close()
	end
end

-- Documenta cada extensión y prueba en workflow-log.md

-- Ejemplo de documentación:
-- [2025-11-08] Se añadió la función logTrainData para registrar velocidad, posición, acelerador y freno en un archivo externo.
-- [2025-11-08] Prueba: Ejecutar logTrainData("C:/Users/doski/TrainSimulatorAutopilot/data/raw/train_log.txt") durante una sesión de simulación.
-- [2025-11-08] Resultado: Se generó el archivo con registros correctos, listo para análisis IA.

-- Recomendación: Cada vez que modifiques este script, agrega una línea de documentación aquí y en docs/workflow-log.md para mantener trazabilidad y orden.