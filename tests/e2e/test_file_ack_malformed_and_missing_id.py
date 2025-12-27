import json
import pytest
pytest.skip("ACK-based flows removed — PoC deprecated and removed from project.", allow_module_level=True)

import os

from tools.poc_file_ack.consumer import Consumer
from tools.poc_file_ack.enqueue import atomic_write_cmd, wait_for_ack


def test_malformed_and_missing_id_handling(tmp_path):
    d = str(tmp_path)
    # malformed JSON file
    with open(os.path.join(d, 'cmd-bad.json'), 'w', encoding='utf-8') as f:
        f.write('not a json')
    # missing id
    with open(os.path.join(d, 'cmd-noid.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps({'type': 'set_regulator', 'value': 0.3}))
    # good command
    cid = atomic_write_cmd(d, {'type': 'set_regulator', 'value': 0.4})

    c = Consumer(d, poll_interval=0.01, process_time=0.01)
    c.start()
    try:
        ack = wait_for_ack(d, cid, timeout=2.0, poll=0.01)
        assert ack is not None
        # bad files should be removed
        assert not os.path.exists(os.path.join(d, 'cmd-bad.json'))
        assert not os.path.exists(os.path.join(d, 'cmd-noid.json'))
    finally:
        c.stop()
        c.join()
