from ai_autopilot.scripts.labeler import label_snapshot
from ai_autopilot.scripts.record_session import parse_getdata


def test_parse_basic():
    lines = [
        "ControlType:Speed\n",
        "ControlName:CurrentSpeed\n",
        "ControlMin:0\n",
        "ControlMax:2\n",
        "ControlValue:10.0\n",
    ]
    raw = parse_getdata(lines)
    assert raw["CurrentSpeed"] == 10.0


def test_labels_basic():
    snapshot = {"controls": {"TrainBrakeControl": 0.5, "CurrentSpeed_kmh": 0.0}}
    labels = label_snapshot(snapshot)
    assert labels["brake_applied"] == 1
    assert labels["is_stopped"] == 1
