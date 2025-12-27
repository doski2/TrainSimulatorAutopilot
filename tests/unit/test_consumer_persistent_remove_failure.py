import pytest
pytest.skip("ACK PoC deprecated — skipping consumer tests.", allow_module_level=True)

import logging
import time

from tools.poc_file_ack.consumer import Consumer
from tools.poc_file_ack.enqueue import atomic_write_cmd


def test_consumer_logs_error_on_persistent_remove_failure(tmp_path, caplog):
    caplog.set_level(logging.ERROR)
    d = str(tmp_path)

    cmd_id = 'persistent-1'
    atomic_write_cmd(d, {'id': cmd_id, 'type': 'set_regulator', 'value': 0.7})

    # monkeypatch os.remove to always raise for this specific command file
    import os as _os
    original_remove = _os.remove

    def always_fail(path):
        if path.endswith(f'cmd-{cmd_id}.json'):
            raise OSError('simulate persistent inability to remove file')
        return original_remove(path)

    _os.remove = always_fail

    try:
        # use low threshold to speed up the test
        c = Consumer(d, poll_interval=0.01, process_time=0.01, removal_failure_threshold=2)
        c.start()
        # allow multiple polling attempts
        time.sleep(0.25)
        c.stop()
        c.join(timeout=1)

        # check logs for persistent failure message
        messages = [r.getMessage() for r in caplog.records]
        assert any('Persistent failure removing' in m for m in messages), messages
    finally:
        _os.remove = original_remove
