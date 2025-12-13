# Data received from Railworks

Archivo con variables y mapeos recibidos desde Train Simulator Classic
(Railworks). Este archivo fue renombrado desde `Data received from
Railworks.txt` para ser visible en MkDocs.

```plaintext
// DATOS DE TELEMETRÍA DE TRAIN SIMULATOR CLASSIC
// Archivo generado por Railworks_GetData_Script.lua
// Actualizado: 2025-12-02

// CONTROLES DE MOTOR Y POTENCIA (NUEVOS - Dashboard v2.0)
TractiveEffort: 0          // [IMPLEMENTADO] Fuerza de tracción en Newtons 0 = sin tracción)
RPM: 318.0007              // [IMPLEMENTADO] Revoluciones por minuto del motor diésel/eléctrico (clamped 0..5000)
RPMDelta: 0                // [NO RELEVANTE] Valor binario para medición de aceleración
CompressorState: 0         // [NO RELEVANTE] Estado del compresor
Wheelslip: 1               // [IMPLEMENTADO] Indicador de deslizamiento de ruedas 0=adherencia perfecta, 1=normal, 1.1-2=deslizamiento)
Ammeter: 0                 // [IMPLEMENTADO] Corriente eléctrica en Amperes (detecta alias: Ammeter/Amps/Amperes/Current). Positiva=generando, negativa=consumiendo. (ControlMin ahora permite valores negativos)

// ... (se conserva todo el contenido original del .txt) ...
```

Nota: El archivo original `Data received from Railworks.txt` ha sido renombrado
para presentarse correctamente en el sitio de MkDocs.
