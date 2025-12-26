import os

from tools.poc_file_ack.consumer import Consumer
from tools.poc_file_ack.enqueue import atomic_write_cmd, wait_for_ack


def test_duplicate_command_processed_once(tmp_path):
    d = str(tmp_path)
    cid = 'dup-e2e'
    # write duplicate commands (same id)
    atomic_write_cmd(d, {'id': cid, 'type': 'set_regulator', 'value': 0.1})
    atomic_write_cmd(d, {'id': cid, 'type': 'set_regulator', 'value': 0.2})

    c = Consumer(d, poll_interval=0.01, process_time=0.01)
    c.start()
    try:
        ack = wait_for_ack(d, cid, timeout=2.0, poll=0.01)
        assert ack is not None
        ack_files = list(tmp_path.glob(f'ack-{cid}*.json')) if 'tmp_path' in globals() else [f for f in os.listdir(d) if f.startswith(f'ack-{cid}')]
        # ensure only one ack file exists for the id
        assert len(ack_files) == 1
    finally:
        c.stop()
        c.join()
