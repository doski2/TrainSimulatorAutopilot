# Autopilot → Tracción y detección de patinaje (slip)

Resumen:

- Documento que describe alternativas para detectar y mitigar el patinaje
  (slip) en el tren, con ejemplos, parámetros recomendados, pseudocódigo,
  tests sugeridos y el camino recomendado para implementación.

## Objetivo 🎯

Detectar cuando una rueda patina y aplicar una respuesta segura y
medible (reducción de aceleración, freno dinámico, aplicación de sand,
etc.), minimizando falsos positivos y manteniendo seguridad operativa.

## Señales y features principales 🔍

- `speed_train` (m/s) — velocidad tierra (ground speed)
- `speed_wheel` (m/s) — velocidad de eje/rueda
- `commanded_throttle` (0..1)
- `measured_tractive_effort` (kN u unidad local)
- `brake_pressure`
- `track_condition` (opcional: `wet`/`ice`/`dry`)
- `timestamp`

Feature básico:

- `slip_ratio = (speed_wheel - speed_train) / max(speed_train, eps)`

Alternativa basada en esfuerzo:

- `expected_effort = f(commanded_throttle, speed_train)`
- `effort_residual = measured_tractive_effort - expected_effort`

---

## Opciones disponibles (resumen y ejemplos) ✅

### 1) Regla simple (EWMA + umbral estático)

- Descripción: calcular `slip_ratio`, suavizar con EWMA y disparar si
  supera `SLIP_THRESHOLD` durante `DEBOUNCE_SEC`.
- Pros: simple, determinista y fácil de probar.
- Contras: puede generar falsos positivos en condiciones cambiantes.
- Parámetros (ejemplo):
  - `SLIP_THRESHOLD = 0.10` (10%)
  - `DEBOUNCE_SEC = 0.5`
  - `RECOVERY_THRESHOLD = 0.05`
  - `RECOVERY_SEC = 1.0`
  - `EWMA_alpha = 0.3`
- Ejemplo: `speed_train = 20 m/s`, `speed_wheel = 22.5 m/s` →
  `slip_ratio = 0.125` → tras `DEBOUNCE_SEC` detecta patinaje.
- Tests: series sintéticas que cruzan el umbral; ruidos breves que no
  disparan; integración con simulate_lua.

### 2) Umbral adaptativo (estadístico: mu + k*sigma)

- Descripción: mantener ventana (p. ej. 60s), calcular `mu`/`sigma` y fijar
  `SLIP_THRESHOLD = mu + K*sigma`.
- Pros: se adapta a condiciones locales y reduce falsos positivos.
- Contras: necesita ventana estable y puede tardar en ajustar tras un
  cambio súbito.
- Parámetros: `WINDOW_SEC = 60`, `K = 3`, `MIN_SAMPLES = 50`.
- Ejemplo: ventana `mu=0.02`, `sigma=0.01` → umbral `0.05`.
- Tests: adaptación tras ventana y fallback si hay pocos datos.

### 3) Detección por residuo (modelo de esfuerzo esperado)

- Descripción: estimar `expected_effort` y detectar grandes residuos
  (`residual`) respecto a la distribución histórica (z-score).
- Pros: detecta fallos físicos donde la tracción no produce avance.
- Contras: requiere ajustar/regresar `f()` con datos.
- Parámetros: `z_thresh = 3.0`, ventana para `mu/sigma` del residual.
- Ejemplo: `expected=100 kN`, `measured=150 kN` → residual `50 kN`
  grande → anómalo.
- Tests: residuals sintéticos y casos de throttle alto sin avance.

### 4) Clasificador incremental (ML online)

- Descripción: modelo supervisado incremental (p. ej. `SGDClassifier`)
  con features: `[slip_ratio, derivative, effort_residual, throttle,
  speed]` y `partial_fit` online.
- Pros: aprende patrones complejos y mejora con más datos.
- Contras: requiere dataset etiquetado y pipeline de reentrenamiento.
- Parámetros: `p_thresh` (prob. de activar), modelo y regularización.
- Tests: entrenar offline con dataset simulado; pruebas de inferencia
  online con `partial_fit`.

### 5) Híbrido (Recomendado para transición) 🔁

- Descripción: arrancar con la **Regla simple** (1) para producción y
  simultáneamente **recoger datos etiquetados** para entrenar/activar
  `Umbral adaptativo` o `Clasificador incremental` más adelante.
- Pros: despliegue rápido y seguro; camino hacia ML sin riesgos grandes.
- Contras: requiere infra de recolección y validación de datos.

---

## Parámetros por defecto recomendados

- `SLIP_THRESHOLD = 0.10`
- `DEBOUNCE_SEC = 0.5`
- `RECOVERY_THRESHOLD = 0.05`
- `RECOVERY_SEC = 1.0`
- `EWMA_alpha = 0.3`
- `ADAPTIVE_WINDOW_SEC = 60`
- `ADAPTIVE_K = 3`

---

## Pseudocódigo (versión simple)

```python
# esquema simplificado
class TractionControl:
    def __init__(self, cfg):
        self.slip_eps = 1e-3
        self.ewma = 0.0
        self.alpha = cfg.ewma_alpha
        self.slip_threshold = cfg.slip_threshold
        self.debounce_sec = cfg.debounce_sec
        self.debounce_state = 0.0

    def update_ewma(self, new):
        self.ewma = self.alpha * new + (1 - self.alpha) * self.ewma
        return self.ewma

    def detect_slip(self, speed_train, speed_wheel, dt):
        slip_ratio = (speed_wheel - speed_train) / max(speed_train, self.slip_eps)
        s = self.update_ewma(slip_ratio)
        if s > self.slip_threshold:
            self.debounce_state += dt
            if self.debounce_state >= self.debounce_sec:
                return True
        else:
            self.debounce_state = 0.0
        return False

    def compute_throttle_adjustment(self, throttle, slip):
        if slip:
            return max(0.0, throttle * (1 - cfg.reduction_factor))
        return throttle
```

---

## Tests y métricas sugeridas 📏

- **Unit tests**:
  - `test_detect_slip_debounce` (serie estable → detect True)
  - `test_no_false_positive_on_spike` (spike corto → detect False)
  - `test_recovery_threshold`
- **Integration / e2e**:
  - `simulate_lua` genera wheel speed > train speed → comprobar
    `SendCommand.txt`/`autopilot_commands.txt` contengan comandos de
    ajuste.
- **Métricas**:
  - `traction_slip_total`, `traction_recover_total`, `traction_falsepos_rate`,
    `time_to_recover`.

---

## Integración y checklist para PR 🔧

- [ ] `lib/traction_control.py` o `autopilot/traction_control.py` con
  funciones públicas y tipado.
- [ ] `tests/unit/test_traction_detect.py` (unitario) y
  `tests/e2e/test_traction_simulated.py` (simulate_lua).
- [ ] Documentación: `docs/AUTOPILOT_TRACTION.md` (este archivo).
- [ ] Actualizar `config.ini.example` con parámetros por defecto.

---

## Recomendación y siguientes pasos ✅

- Implementar **Regla simple** (opción 1) primero: rápido de probar y
  seguro para producción.
- Añadir recolección de telemetría para evolucionar a un umbral
  adaptativo o a un clasificador incremental (opciones 2–4).
- Crear PR con código, tests y docs; ejecutar `pytest` y `ruff`.

Si quieres, empiezo ahora creando la implementación básica (archivo +
unit tests + e2e simulate) y abro el PR en la rama actual.

---

*Documento generado por GitHub Copilot (Raptor mini — Preview).*
