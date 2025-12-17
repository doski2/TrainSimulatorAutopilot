import os
import tempfile
import subprocess

from tools.poc_file_ack.enqueue import atomic_write_cmd, wait_for_ack
from tools.poc_file_ack.consumer import Consumer



def test_enqueue_and_ack():
    with tempfile.TemporaryDirectory() as d:
        c = Consumer(d, poll_interval=0.01, process_time=0.01)
        c.start()
        try:
            cmd_id = atomic_write_cmd(d, {'type': 'set_regulator', 'value': 0.4})
            ack = wait_for_ack(d, cmd_id, timeout=2.0)
            assert ack is not None
            assert ack.get('id') == cmd_id
            assert ack.get('status') == 'applied'
        finally:
            c.stop()
            c.join()
