# Propuestas de control (software-only)

Resumen de alternativas para permitir que la IA controle el tren sin hardware.
Para cada propuesta incluyo descripción, ejemplos de uso,
ventajas y desventajas.

---

## 1) Protocolo basado en archivos con ACK

(archivos: `autopilot_commands.txt` + `autopilot_state.txt`)

- Descripción: Python escribe comandos en un archivo. El plugin Lua los consume
  y escribe un fichero de confirmación (ACK) cuando procesa el comando.
- Ejemplo de comando (línea por línea):
  - `{"cmd":"start_autopilot"}\n`
  - `Regulator:0.400` (compatibilidad con SendCommand)
- Ventajas:
  - Muy fácil de implementar y probar.
  - Funciona en plataformas con acceso a sistema de archivos (Windows).
  - Buena trazabilidad (archivos persistentes para depuración).
  - No requiere drivers ni permisos especiales.
    (Solo escritura/lectura de archivos en carpeta de plugins
    o en una carpeta compartida).
- Desventajas:
  - Latencia/buffering depende del polling del script en el juego.
  - Requiere que el script Lua esté cargado y tenga permisos de I/O.
  - Posible contención/concursos si no se hace escritura atómica.
- Recomendación: Probar y robustecer con cola, timeouts y reintentos;
  usar ACK con timestamps y IDs.

---

## 2) Uso de SendCommand / SendCommand.txt (compatibilidad RailDriver)

- Descripción: Escribir líneas en el formato que el juego o los
  plugins esperan (ej. `Regulator:0.400`) en `SendCommand.txt` o
  `sendcommand.txt`.
- Ejemplo:
  - `Regulator:0.400` → regula el acelerador
- Ventajas:
  - Compatibilidad con mapeos existentes.
    (RailDriver y algunos plugins leen SendCommand).
  - Integración sencilla con soluciones ya existentes en la comunidad.
- Desventajas:
  - Limitado al conjunto de comandos que el juego reconoce.
  - Sin semántica rica.
    (Difícil de confirmar que el comando fue aplicado: falta ACK nativo).
- Recomendación: Usar en combinación con el método 1 (archivo+ACK)
  para confirmar ejecución.

---

## 3) Emulación de joystick/teclado (vJoy + pyvjoy / SendInput)

- Descripción: Crear un dispositivo de joystick virtual (vJoy) y enviar eventos
  de eje/botón desde Python; el juego recibe estos eventos como input humano.
- Ejemplo (pyvjoy, pseudocódigo):
  - `joystick.set_axis(pyvjoy.HID_USAGE_X, value)`
- Ventajas:
  - Muy compatible con juegos que no exponen API de control directo.
  - Baja latencia; el juego trata los eventos como inputs reales.
- Desventajas:
  - Requiere instalar drivers (vJoy) y permisos de admin en algunos casos.
  - Más difícil de mapear a acciones de alto nivel.
    (Ej.: una maniobra de frenado controlada requiere
    control fino y lógica adicional).
  - Más difícil de probar en CI / automatización.
- Recomendación: Buena segunda opción si los plugins no pueden ser
  modificados; añadir una capa que traduzca comandos de alto nivel a
  eventos de ejes/botones.

---

## 4) Puente vía feeder para vJoy

(vJoySerialFeeder / feeder por puerto serial)

- Descripción: Usar un «feeder» que reciba comandos por TCP/Serial
  y traduzca a vJoy.
- Ventajas:
  - Aísla la parte de red/AI de la emulación de joystick.
  - Permite control remoto sin cambiar el juego.
- Desventajas:
  - Dependencias adicionales; más componentes a mantener.

---

## 5) Plugin de red (TCP/UDP) dentro del juego (plugin Lua o C++)

- Descripción: Implementar en el plugin del juego un servidor ligero que acepte
  comandos por TCP/UDP (o WebSocket) y los ejecute directamente, devolviendo
  ACK por la misma conexión.
- Ejemplo:
  - `echo '{"cmd":"Regulator","value":0.4}' | nc host port`
- Ventajas:
  - Baja latencia y ACKs inmediatos.
  - Más directo y más fácil de coordinar con controladores externos.
- Desventajas:
  - Lua en Train Simulator puede no soportar sockets nativamente.
    (Puede requerir módulos extra, compilación en C o uso de FFI, y por
    tanto un plugin nativo.)
  - Riesgos de seguridad (abrir puertos en la máquina del cliente).
- Recomendación: Evaluar si el motor soporta sockets; si no,
  esta opción puede ser compleja.

---

## 6) Uso de un servicio externo + UI de control (HTTP REST)

- Descripción: Implementar un servicio HTTP local en Python que la IA llame;
  el servicio escribe a los canales (archivos, vJoy, sockets).
- Ventajas:
  - Muy estructurado, fácil de instrumentar, y permite
    autenticación/telemetría.
  - Escalable a múltiples agentes y módulos (CLI, UI, cron jobs).
- Desventajas:
  - Aún depende de cómo el juego consume comandos (archivo, vJoy, plugin).
- Recomendación: Muy buena para orchestrar lógica; combinar con ACK
  (archivo o socket) para verificación.

---

## 7) Instrumentación GetData (fallback de lectura)

- Descripción: Añadir código al GetData.lua existente para detectar
  comandos en `autopilot_commands.txt` y aplicarlos.
- Ventajas:
  - Permite que la integración exista incluso si el plugin
    principal de autopilot no se carga.
  - Fácil de desplegar como parche de escenario.
- Desventajas:
  - Puede no cubrir todos los casos y requiere pruebas en múltiples escenarios.
- Recomendación: Útil como mecanismo de resilencia mientras se
  estabiliza el plugin principal.

---

## 8) Técnicas avanzadas (memoria, hooking) — no recomendadas

- Descripción: Leer/editar memoria del proceso o inyectar hooks para
  alterar estados del simulador.
- Ventajas: Control muy directo.
- Desventajas: Código frágil, arriesga integridad del juego,
  potencialmente prohibido por TOS y difícil de mantener.
- Recomendación: Evitar salvo como último recurso y con consentimiento claro.

---

## Comparación rápida (resumen)

|Método|Perm.|Lat.|Rob.|Fac.|Recomendado|
|---|---:|---:|---:|---:|---:|---|
|Archivo+ACK|bajo|medio|alto|muy fácil|integración|
|SendCommand|bajo|medio|medio|fácil|mapeos|
|vJoy|medio|baja|alta|medio|fallback|
|Socket|medio-alto|muy baja|alta|difícil|baja-latencia|
|HTTP|bajo|depende|alta|fácil|orquestación|

---

## Ejemplos de formatos (rápidos)

- Línea JSON (archivo):

```json
{
  "id": "cmd-001",
  "type": "set_regulator",
  "value": 0.4,
  "ts": 1700000000
}
```

- Línea legacy (SendCommand):

```text
Regulator:0.400
```

- ACK esperado (archivo):

```json
{
  "id": "cmd-001",
  "status": "applied",
  "ts": 1700000001
}
```

---

## Próximos pasos sugeridos

1. Priorizar 2–3 alternativas para prototipar (por ejemplo: Archivo+ACK,
   SendCommand compatibilidad y vJoy como fallback).
2. Implementar pruebas end-to-end pequeñas para cada una (scripts que envíen
   comandos y verifiquen ACK o efectos observables).
3. Medir latencia, confiabilidad y casos límite (escenarios con alto churn
   de comandos).
4. Elegir la(s) solución(es) a mantener y documentar API/formatos.

---

Si quieres, puedo:

- Añadir ejemplos de código concretos (snippets de Python y Lua)
  para cualquiera de las propuestas.
- Crear pruebas de POC (pequeños tests) para probar las 2–3
  alternativas priorizadas.

Indica qué propuestas priorizamos y preparo los POCs. ✅
