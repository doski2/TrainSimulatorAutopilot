import pytest
pytest.skip("ACK PoC deprecated — skipping consumer tests.", allow_module_level=True)

import os
import time

from tools.poc_file_ack.consumer import Consumer
from tools.poc_file_ack.enqueue import atomic_write_cmd


def test_consumer_recreates_missing_directory_and_continues(tmp_path):
    d = str(tmp_path)
    # create and then delete the directory while consumer runs
    os.makedirs(d, exist_ok=True)
    c = Consumer(d, poll_interval=0.01, process_time=0.01)
    c.start()
    try:
        # remove directory to simulate external cleanup
        time.sleep(0.05)
        import shutil
        shutil.rmtree(d)
        # wait a bit for consumer to detect and recreate
        time.sleep(0.2)
        # now enqueue a command using atomic writer (should recreate dir if was deleted)
        cid = atomic_write_cmd(d, {'type': 'set_regulator', 'value': 0.5})
        # wait for ack
        time.sleep(0.2)
        ack_path = os.path.join(d, f'ack-{cid}.json')
        assert os.path.exists(ack_path)
    finally:
        c.stop()
        c.join(timeout=1)
