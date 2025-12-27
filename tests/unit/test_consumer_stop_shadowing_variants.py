import pytest
pytest.skip("ACK PoC deprecated — skipping consumer tests.", allow_module_level=True)

import threading
import time

from tools.poc_file_ack.consumer import Consumer


def test_consumer_handles_classlevel__stop_shadowing(tmp_path):
    d = str(tmp_path)
    # simulate old code setting a non-callable _stop at the class level
    Consumer._stop = threading.Event()  # type: ignore[attr-defined]
    try:
        c = Consumer(d, poll_interval=0.01, process_time=0.01)
        c.start()
        time.sleep(0.05)
        c.stop()
        c.join(timeout=1)
        assert not c.is_alive()
    finally:
        # cleanup to avoid affecting other tests
        try:
            delattr(Consumer, '_stop')
        except Exception:
            pass


def test_consumer_handles_instance__stop_shadowing_after_start(tmp_path):
    d = str(tmp_path)
    c = Consumer(d, poll_interval=0.01, process_time=0.01)
    c.start()
    # simulate someone setting a non-callable instance attribute after start
    c._stop = threading.Event()  # type: ignore[attr-defined]
    time.sleep(0.05)
    c.stop()
    c.join(timeout=1)
    assert not c.is_alive()
