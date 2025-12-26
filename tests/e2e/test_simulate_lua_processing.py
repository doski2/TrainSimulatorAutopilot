import importlib.util
from pathlib import Path

# The tests use the helper function implemented in .github/scripts/simulate_lua.py


# Dynamically import the simulate_lua module from .github/scripts
spec = importlib.util.spec_from_file_location(
    "simulate_lua",
    Path(__file__).resolve().parents[2] / ".github" / "scripts" / "simulate_lua.py",
)
# spec_from_file_location can return None on failure; assert to satisfy type checkers
assert spec is not None, "unable to locate simulate_lua script"
# module_from_spec requires a non-None ModuleSpec
simulate_lua = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(simulate_lua)  # type: ignore


def test_start_autopilot_writes_ack_and_removes_file(tmp_path):
    plugins = tmp_path
    cmd_file = plugins / "autopilot_commands.txt"
    cmd_file.write_text("start_autopilot\n", encoding="utf-8")

    simulate_lua.process_commands_file(plugins)

    # Commands file should be removed
    assert not cmd_file.exists()

    # ACK file should be present and contain 'on'
    ack = plugins / "autopilot_state.txt"
    assert ack.exists()
    assert ack.read_text(encoding="utf-8").strip() == "on"

    # Debug log contains processing entry
    dbg = plugins / "autopilot_debug.log"
    assert dbg.exists()
    assert "processing start_autopilot" in dbg.read_text(encoding="utf-8")


def test_control_value_parsing_logs_numeric_and_boolean(tmp_path):
    plugins = tmp_path
    content = "Regulator:0.5\nHeadlights:true\nBadLineWithoutColon\nBadControl:weirdvalue\n"
    (plugins / "autopilot_commands.txt").write_text(content, encoding="utf-8")

    simulate_lua.process_commands_file(plugins)

    # Commands file removed
    assert not (plugins / "autopilot_commands.txt").exists()

    dbg = plugins / "autopilot_debug.log"
    txt = dbg.read_text(encoding="utf-8")
    # Numeric parsed
    assert "parsed control -> Regulator:0.5" in txt
    # Boolean parsed
    assert "parsed control -> Headlights:true" in txt
    # Bad line without colon should be logged as failed to parse
    assert "failed to parse control line -> BadLineWithoutColon" in txt
    # Unrecognized control format for weirdvalue
    assert "unrecognized control format -> BadControl:weirdvalue" in txt


def test_predictive_state_toggle(tmp_path):
    plugins = tmp_path
    (plugins / "autopilot_commands.txt").write_text("start_predictive\nstop_predictive\n", encoding="utf-8")

    simulate_lua.process_commands_file(plugins)

    # The last state written should be 'off'
    pred = plugins / "predictive_state.txt"
    assert pred.exists()
    assert pred.read_text(encoding="utf-8").strip() == "off"
