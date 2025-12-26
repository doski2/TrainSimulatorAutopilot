#!/usr/bin/env python3
"""Monitor simple de patinaje (slip) para ejecutar con Train Simulator.

- Lee un archivo de telemetría (por defecto `GetData.txt`) que debe
  contener JSON por línea con, al menos, los campos
  `speed_train`, `speed_wheel` y `throttle`.
- Calcula `slip_ratio` con EWMA y aplica debounce.
- Si detecta patinaje, reduce throttle y escribe comandos en
  `SendCommand.txt` y `autopilot_commands.txt`.

Uso:
  python scripts/monitor_slip_example.py --getdata path/to/GetData.txt
  python scripts/monitor_slip_example.py --getdata path/to/GetData.txt --simulate

Nota: el modo `--simulate` genera líneas de telemetría sintética para
probar detección incluso si no tienes condiciones de patinaje reales.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

# Parámetros por defecto (ajustables)
SLIP_THRESHOLD = 0.10  # 10%
DEBOUNCE_SEC = 0.5
RECOVERY_THRESHOLD = 0.05
RECOVERY_SEC = 1.0
EWMA_ALPHA = 0.3
REDUCTION_FACTOR = 0.5
POLL_INTERVAL = 0.1  # s


def update_ewma(old: float, new: float, alpha: float) -> float:
    return alpha * new + (1 - alpha) * old


class SlipDetector:
    def __init__(self, cfg: dict[str, Any]):
        self.e = cfg.get("ewma_init", 0.0)
        self.alpha = cfg.get("ewma_alpha", EWMA_ALPHA)
        self.slip_threshold = cfg.get("slip_threshold", SLIP_THRESHOLD)
        self.debounce_sec = cfg.get("debounce_sec", DEBOUNCE_SEC)
        self.recovery_threshold = cfg.get("recovery_threshold", RECOVERY_THRESHOLD)
        self.recovery_sec = cfg.get("recovery_sec", RECOVERY_SEC)
        self.debounce_state = 0.0
        self.recovery_state = 0.0

    def step(self, slip_ratio: float, dt: float) -> bool:
        self.e = update_ewma(self.e, slip_ratio, self.alpha)
        if self.e > self.slip_threshold:
            self.debounce_state += dt
            self.recovery_state = 0.0
            if self.debounce_state >= self.debounce_sec:
                return True
        else:
            # not slipping: progress recovery
            if self.e < self.recovery_threshold:
                self.recovery_state += dt
                if self.recovery_state >= self.recovery_sec:
                    self.debounce_state = 0.0
            else:
                self.recovery_state = 0.0
            self.debounce_state = 0.0
        return False


def write_command_file(path: Path, line: str) -> None:
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(line.rstrip() + "\n")
    except Exception as e:
        print(f"[ERROR] Escritura en {path}: {e}")


def reduce_throttle(throttle: float) -> float:
    return max(0.0, throttle * (1 - REDUCTION_FACTOR))


def parse_latest_json_line(path: Path) -> dict | None:
    try:
        if not path.exists():
            return None
        # Leemos todo y tomamos la última línea no vacía
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f if l.strip()]
        if not lines:
            return None
        last = lines[-1]
        try:
            return json.loads(last)
        except json.JSONDecodeError:
            # No es JSON: intentar parsear claves separadas por comas (deprecated)
            return None
    except Exception as e:
        print(f"[ERROR] Leyendo {path}: {e}")
        return None


def simulate_telemetry(getdata: Path, duration: float = 5.0) -> None:
    """Genera telemetría sintética que induce patinaje para pruebas."""
    t0 = time.time()
    while time.time() - t0 < duration:
        # alternar entre normal y patinaje
        now = time.time() - t0
        if now < duration / 2:
            # normal
            rec = {
                "speed_train": 15.0,
                "speed_wheel": 15.0,
                "throttle": 0.6,
            }
        else:
            # patinaje: wheel speed más alta que ground speed
            rec = {
                "speed_train": 15.0,
                "speed_wheel": 17.5,
                "throttle": 0.9,
            }
        with getdata.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        time.sleep(POLL_INTERVAL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--getdata", required=True, help="Ruta a GetData.txt")
    parser.add_argument("--sendcommand", default=None, help="Ruta a SendCommand.txt (opcional)")
    parser.add_argument("--autocommands", default=None, help="Ruta a autopilot_commands.txt (opcional)")
    parser.add_argument("--simulate", action="store_true", help="Generar telemetría sintética para probar")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    getdata = Path(args.getdata)
    sendcommand = Path(args.sendcommand) if args.sendcommand else None
    auto_commands = Path(args.autocommands) if args.autocommands else None

    detector = SlipDetector({
        "ewma_alpha": EWMA_ALPHA,
        "slip_threshold": SLIP_THRESHOLD,
        "debounce_sec": DEBOUNCE_SEC,
        "recovery_threshold": RECOVERY_THRESHOLD,
        "recovery_sec": RECOVERY_SEC,
    })

    if args.simulate:
        print("[INFO] Modo simulate: generando telemetría sintética (5s)")
        simulate_telemetry(getdata)
        print("[INFO] Simulación terminada; ahora arrancando monitor")

    last_ts = time.time()
    print(f"[INFO] Monitor de patinaje escuchando {getdata}")

    try:
        while True:
            t0 = time.time()
            data = parse_latest_json_line(getdata)
            if data:
                st = data.get("speed_train")
                sw = data.get("speed_wheel")
                throttle = float(data.get("throttle", 0.0))
                if st is None or sw is None:
                    if args.verbose:
                        print("[DEBUG] Telemetría incompleta, esperando...")
                else:
                    slip_ratio = (sw - st) / max(st, 1e-3)
                    dt = max(1e-6, t0 - last_ts)
                    last_ts = t0
                    slipping = detector.step(slip_ratio, dt)
                    if slipping:
                        new_th = reduce_throttle(throttle)
                        msg = f"set_throttle {new_th:.2f}  # detected slip {slip_ratio:.3f}"
                        print(f"[ACTION] {msg}")
                        if sendcommand:
                            write_command_file(sendcommand, msg)
                        if auto_commands:
                            write_command_file(auto_commands, msg)
                    else:
                        if args.verbose:
                            print(f"[OK] slip_ratio={slip_ratio:.3f} ewma={detector.e:.3f}")
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("[INFO] Monitor detenido por el usuario")


if __name__ == "__main__":
    main()
