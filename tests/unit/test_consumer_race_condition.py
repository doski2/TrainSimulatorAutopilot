import pytest
pytest.skip("PoC deprecated — skipping consumer tests.", allow_module_level=True)

import json
import logging
import time

from tools.poc_file_ack.consumer import Consumer
from tools.poc_file_ack.enqueue import atomic_write_cmd


def test_consumer_marks_processed_before_ack_and_does_not_reprocess(tmp_path, caplog):
    caplog.set_level(logging.INFO)
    d = str(tmp_path)

    # create a command file
    cmd_id = 'race-1'
    atomic_write_cmd(d, {'id': cmd_id, 'type': 'set_regulator', 'value': 0.5})

    # monkeypatch os.remove to fail the first time a specific cmd file is removed
    import os as _os

    original_remove = _os.remove
    calls = {'n': 0}

    def flaky_remove(path):
        # only raise for the specific command file once
        if path.endswith(f'cmd-{cmd_id}.json') and calls['n'] == 0:
            calls['n'] += 1
            raise OSError('simulate inability to remove file')
        return original_remove(path)

    _os.remove = flaky_remove

    try:
        # start consumer; it should process, write ack, attempt to remove and fail (we simulate)
        c = Consumer(d, poll_interval=0.01, process_time=0.01)
        c.start()
        time.sleep(0.2)
        c.stop()
        c.join(timeout=1)

        # confirmation file should exist
        conf_path = tmp_path / f'ack-{cmd_id}.json'
        assert conf_path.exists(), 'confirmation file should have been written'

        # processed_ids should include cmd_id (persisted)
        processed_file = tmp_path / 'processed_ids.json'
        assert processed_file.exists(), 'processed_ids.json should exist'
        with open(processed_file, encoding='utf-8') as f:
            data = json.load(f)
        assert cmd_id in data

        # start a new consumer; it should load processed_ids and remove the leftover cmd file without creating a second ack
        c2 = Consumer(d, poll_interval=0.01, process_time=0.01)
        c2.start()
        time.sleep(0.2)
        c2.stop()
        c2.join(timeout=1)

        # ensure there's only one ack file for cmd_id
        ack_files = list(tmp_path.glob(f'ack-{cmd_id}*.json'))
        assert len(ack_files) == 1, f'expected 1 ack file, found {len(ack_files)}'

        # command file should now be removed
        cmd_path = tmp_path / f'cmd-{cmd_id}.json'
        assert not cmd_path.exists(), 'command file should have been removed by second consumer'

    finally:
        # restore os.remove
        _os.remove = original_remove
