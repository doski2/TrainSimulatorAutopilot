import pytest
pytest.skip("ACK-based flows removed — PoC deprecated and removed from project.", allow_module_level=True)

from tools.poc_file_ack.enqueue import atomic_write_cmd, wait_for_ack


def test_wait_for_ack_times_out(tmp_path):
    d = str(tmp_path)
    cmd_id = atomic_write_cmd(d, {'type': 'set_regulator', 'value': 0.1})
    ack = wait_for_ack(d, cmd_id, timeout=0.2, poll=0.01)
    assert ack is None
