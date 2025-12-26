"""Simulate the Lua plugin readPythonCommands behavior for testing and CI.

This helper reads <plugins_dir>/autopilot_commands.txt, processes simple directive lines
(start_autopilot, stop_autopilot, start_predictive, stop_predictive, emergency_brake,
lights_on/lights_off) and control:value lines. It writes ack files (autopilot_state.txt,
predictive_state.txt) and logs parsed lines to autopilot_debug.log to mirror the Lua
script behavior for tests.

This file is intended for testing and CI only; it intentionally reimplements a subset of
`complete_autopilot_lua.lua:readPythonCommands` so tests can assert end-to-end file-based
interactions without requiring a running Lua environment.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable


def _append_debug_log(plugins_dir: Path, message: str) -> None:
    log_file = plugins_dir / "autopilot_debug.log"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def process_commands_file(plugins_dir: Path) -> None:
    """Process the file <plugins_dir>/autopilot_commands.txt if present.

    Mirrors Lua behavior: trims lines, processes directive tokens, handles
    control:value pairs (numbers and booleans) and deletes the input file when done.
    """
    cmd_file = plugins_dir / "autopilot_commands.txt"
    if not cmd_file.exists():
        return

    with cmd_file.open("r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f.readlines()]

    for line in lines:
        if not line:
            continue
        if line == "start_autopilot":
            (plugins_dir / "autopilot_state.txt").write_text("on", encoding="utf-8")
            _append_debug_log(plugins_dir, "readPythonCommands: processing start_autopilot")
        elif line == "stop_autopilot":
            (plugins_dir / "autopilot_state.txt").write_text("off", encoding="utf-8")
            _append_debug_log(plugins_dir, "readPythonCommands: processing stop_autopilot")
        elif line == "start_predictive":
            (plugins_dir / "predictive_state.txt").write_text("on", encoding="utf-8")
            _append_debug_log(plugins_dir, "readPythonCommands: processing start_predictive")
        elif line == "stop_predictive":
            (plugins_dir / "predictive_state.txt").write_text("off", encoding="utf-8")
            _append_debug_log(plugins_dir, "readPythonCommands: processing stop_predictive")
        elif line == "emergency_brake":
            _append_debug_log(plugins_dir, "readPythonCommands: processing emergency_brake")
            # no ack file for emergency_brake
        elif line == "lights_on":
            _append_debug_log(plugins_dir, "readPythonCommands: processing lights_on")
            (plugins_dir / "autopilot_debug.log").write_text("Lights set: on\n", encoding="utf-8")
        elif line == "lights_off":
            _append_debug_log(plugins_dir, "readPythonCommands: processing lights_off")
            (plugins_dir / "autopilot_debug.log").write_text("Lights set: off\n", encoding="utf-8")
        elif ":" in line:
            # Attempt to parse control:value
            name, value = [part.strip() for part in line.split(":", 1)]
            num = None
            try:
                num = float(value)
            except Exception:
                num = None
            if num is not None:
                _append_debug_log(plugins_dir, f"readPythonCommands: parsed control -> {name}:{num}")
            else:
                low = value.lower()
                if low in ("true", "false"):
                    _append_debug_log(plugins_dir, f"readPythonCommands: parsed control -> {name}:{low}")
                else:
                    _append_debug_log(plugins_dir, f"readPythonCommands: unrecognized control format -> {line}")
        else:
            _append_debug_log(plugins_dir, f"readPythonCommands: failed to parse control line -> {line}")

    # Remove the file after processing (best-effort, mirror Lua behavior)
    try:
        cmd_file.unlink()
        _append_debug_log(plugins_dir, "readPythonCommands: finished processing and removed file")
    except Exception:
        pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("plugins_dir", help="Directory containing plugin files (where autopilot_commands.txt lives)")
    args = parser.parse_args()
    process_commands_file(Path(args.plugins_dir))
