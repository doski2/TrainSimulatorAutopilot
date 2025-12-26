import os
import tempfile
import time

from tools.poc_file_ack.consumer import Consumer


def test_probe_file_written():
    with tempfile.TemporaryDirectory() as d:
        c = Consumer(d, poll_interval=0.01)
        c.start()
        try:
            probe = os.path.join(d, 'plugin_loaded.txt')
            # wait up to 1s for probe file
            end = time.time() + 1.0
            while time.time() < end and not os.path.exists(probe):
                time.sleep(0.01)
            assert os.path.exists(probe), 'probe file not found'
            with open(probe, encoding='utf-8') as f:
                content = f.read().strip()
            assert content.startswith('loaded:'), 'probe content invalid'
        finally:
            c.stop()
            c.join()
