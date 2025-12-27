import pytest
pytest.skip("ACK PoC deprecated — skipping consumer tests.", allow_module_level=True)

import threading
import time

from tools.poc_file_ack.consumer import Consumer


def test_consumer_handles_preexisting__stop_shadowing(tmp_path):
    d = str(tmp_path)
    c = Consumer(d, poll_interval=0.01, process_time=0.01)
    # simulate old code or external actor setting a non-callable _stop
    c._stop = threading.Event()  # type: ignore[attr-defined]
    c.start()
    time.sleep(0.05)
    c.stop()
    c.join(timeout=1)
    assert not c.is_alive()
