import pytest  # noqa: I001
pytest.skip("PoC deprecated — skipping consumer tests.", allow_module_level=True)

import time  # noqa: E402

from tools.poc_file_ack.consumer import Consumer  # noqa: E402


def test_consumer_stop_and_join_does_not_raise(tmp_path):
    d = str(tmp_path)
    c = Consumer(d, poll_interval=0.01, process_time=0.01)
    c.start()
    time.sleep(0.05)
    c.stop()
    # should not raise
    c.join(timeout=1)
    assert not c.is_alive()
