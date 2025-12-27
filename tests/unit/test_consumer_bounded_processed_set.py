import pytest
pytest.skip("ACK PoC deprecated — skipping consumer tests.", allow_module_level=True)

import time

from tools.poc_file_ack.consumer import Consumer
from tools.poc_file_ack.enqueue import atomic_write_cmd


def test_consumer_bounded_processed_set(tmp_path):
    d = str(tmp_path)
    max_ids = 3

    # create 5 commands quickly
    for i in range(5):
        atomic_write_cmd(d, {'id': f'id-{i}', 'type': 'set_regulator', 'value': i})

    # start consumer with small max
    c = Consumer(d, poll_interval=0.01, process_time=0.01, processed_ids_max=max_ids)
    c.start()
    # wait for processing
    time.sleep(0.3)
    c.stop()
    c.join(timeout=1)

    keys = list(c.processed.keys())
    # should keep at most max_ids
    assert len(keys) <= max_ids
    # should contain the most recent ids (id-2, id-3, id-4)
    assert 'id-0' not in keys
    assert 'id-1' not in keys
    assert 'id-2' in keys and 'id-3' in keys and 'id-4' in keys
