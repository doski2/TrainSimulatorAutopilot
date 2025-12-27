import pytest
pytest.skip("ACK-based flows removed — PoC deprecated and removed from project.", allow_module_level=True)

from tools.poc_file_ack.consumer import Consumer
from tools.poc_file_ack.enqueue import atomic_write_cmd, wait_for_ack


def test_many_commands_processed(tmp_path):
    d = str(tmp_path)
    c = Consumer(d, poll_interval=0.01, process_time=0.01)
    c.start()
    try:
        cmd_ids = [atomic_write_cmd(d, {'type': 'set_regulator', 'value': i}) for i in range(10)]
        for cid in cmd_ids:
            ack = wait_for_ack(d, cid, timeout=2.0, poll=0.01)
            assert ack is not None
            assert ack.get('id') == cid
            assert ack.get('status') == 'applied'
    finally:
        c.stop()
        c.join()
