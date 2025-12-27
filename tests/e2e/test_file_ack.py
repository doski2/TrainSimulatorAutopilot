import pytest
pytest.skip("ACK-based flows removed — PoC deprecated and removed from project.", allow_module_level=True)

import os
import subprocess
import tempfile

from tools.poc_file_ack.consumer import Consumer
from tools.poc_file_ack.enqueue import atomic_write_cmd, wait_for_ack


# CI diagnostic: print git HEAD and snippet of consumer.py so remote logs show which version is used.
def _ci_diagnostic():
    try:
        sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.STDOUT).decode().strip()
    except Exception as e:
        sha = f'git rev-parse failed: {e}'
    print(f"CI DIAGNOSTIC: git HEAD: {sha}")
    try:
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'poc_file_ack', 'consumer.py')
        path = os.path.abspath(path)
        with open(path, encoding='utf-8') as f:
            lines = f.readlines()
        print("CI DIAGNOSTIC: consumer.py head:\n" + "".join(lines[:120]))
    except Exception as e:
        print(f"CI DIAGNOSTIC: failed to read consumer.py: {e}")

_ci_diagnostic()


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
