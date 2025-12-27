"""Módulo simple de control de tracción (detector de patinaje)"""
from __future__ import annotations

from dataclasses import dataclass

# Use PEP 604 union operator (`X | None`) for optional types to satisfy Ruff UP045


@dataclass
class TractionConfig:
    slip_threshold: float = 0.10
    debounce_sec: float = 0.5
    recovery_threshold: float = 0.05
    recovery_sec: float = 1.0
    ewma_alpha: float = 0.3
    reduction_factor: float = 0.5


class TractionControl:
    def __init__(self, cfg: TractionConfig | None = None) -> None:
        # Accept either TractionConfig or None (PEP 604 union syntax)
        self.cfg = cfg or TractionConfig()
        self.e = 0.0  # EWMA state for slip_ratio
        self.debounce_state = 0.0
        self.recovery_state = 0.0

    def _update_ewma(self, value: float) -> float:
        a = self.cfg.ewma_alpha
        self.e = a * value + (1 - a) * self.e
        return self.e

    def detect_slip(self, speed_train: float | None, speed_wheel: float | None, dt: float, slip_intensity: float | None = None) -> bool:
        """Actualizar detector con nueva muestra y devolver si hay patinaje.

        Args:
            speed_train: velocidad del tren (m/s) o None
            speed_wheel: velocidad de rueda/axle (m/s) o None
            dt: tiempo (s) desde la muestra anterior
            slip_intensity: intensidad de patinaje normalizada 0..1 (opcional)
        Returns:
            True si hay patinaje detectado (tras debounce).
        """
        # Si se provee slip_intensity, lo usamos directamente como "slip_ratio".
        if slip_intensity is not None:
            slip_ratio = float(slip_intensity)
        else:
            slip_eps = 1e-3
            if speed_train is None or speed_wheel is None:
                # Sin datos suficientes, no declarar patinaje
                return False
            slip_ratio = (speed_wheel - speed_train) / max(speed_train, slip_eps)

        s = self._update_ewma(slip_ratio)

        if s > self.cfg.slip_threshold:
            self.debounce_state += dt
            self.recovery_state = 0.0
            if self.debounce_state >= self.cfg.debounce_sec:
                return True
        else:
            # no longer above threshold; allow recovery
            if s < self.cfg.recovery_threshold:
                self.recovery_state += dt
                if self.recovery_state >= self.cfg.recovery_sec:
                    self.debounce_state = 0.0
            else:
                self.recovery_state = 0.0
            # note: if s below threshold we don't return True
        return False

    def compute_throttle_adjustment(self, current_throttle: float, slip: bool) -> float:
        if slip:
            return max(0.0, current_throttle * (1 - self.cfg.reduction_factor))
        return current_throttle
