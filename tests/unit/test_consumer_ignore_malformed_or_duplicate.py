import json
import logging
import time

from tools.poc_file_ack.consumer import Consumer


def test_consumer_warns_and_removes_malformed_and_duplicate(tmp_path, caplog):
    caplog.set_level(logging.WARNING)
    d = str(tmp_path)

    # malformed (no id) command file
    malformed_path = tmp_path / "cmd-malformed.json"
    with open(malformed_path, "w", encoding="utf-8") as f:
        json.dump({"type": "set_regulator", "value": 0.3}, f)

    # duplicate command file (simulate processed id)
    dup_id = "dup-1"
    dup_path = tmp_path / f"cmd-{dup_id}.json"
    with open(dup_path, "w", encoding="utf-8") as f:
        json.dump({"id": dup_id, "type": "set_regulator", "value": 0.4}, f)

    c = Consumer(d, poll_interval=0.01, process_time=0)
    # inject processed id to simulate duplicate
    c.processed.add(dup_id)
    c._persist_processed_ids()

    c.start()
    time.sleep(0.1)
    c.stop()
    c.join(timeout=1)

    # both files should be removed
    assert not malformed_path.exists(), "malformed command file should be removed"
    assert not dup_path.exists(), "duplicate command file should be removed"

    # warnings should be logged for each case
    messages = [r.getMessage() for r in caplog.records]
    assert any("missing id" in m or "malformed" in m.lower() for m in messages), messages
    assert any("duplicate id" in m for m in messages), messages
