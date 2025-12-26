import tempfile
import threading
import time

from tools.poc_file_ack.consumer import Consumer
from tools.poc_file_ack.enqueue import send_command_with_retries


def test_retries_exhausted_no_consumer():
    with tempfile.TemporaryDirectory() as d:
        # no consumer started
        start = time.time()
        ack = send_command_with_retries(d, {'type': 'set_regulator', 'value': 0.1}, timeout=0.5, retries=2, initial_delay=0.2, backoff=1.5, poll=0.05)
        elapsed = time.time() - start
        assert ack is None
        # total wait should be at least timeout*(retries+1)
        assert elapsed >= 0.5 * (2 + 1) - 0.1


def test_retries_succeeds_when_consumer_starts_late():
    with tempfile.TemporaryDirectory() as d:
        # start a consumer after a short delay so first attempt times out
        def delayed_start():
            time.sleep(0.8)
            c = Consumer(d, poll_interval=0.01, process_time=0.01)
            c.start()
            # stop after a while
            time.sleep(2.0)
            c.stop()
            c.join()

        t = threading.Thread(target=delayed_start, daemon=True)
        t.start()

        ack = send_command_with_retries(d, {'type': 'set_regulator', 'value': 0.2}, timeout=0.4, retries=5, initial_delay=0.2, backoff=1.5, poll=0.05)
        assert ack is not None
        assert ack.get('status') == 'applied'
