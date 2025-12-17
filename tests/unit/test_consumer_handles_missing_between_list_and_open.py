import json
import logging
import time
import builtins
from tools.poc_file_ack.consumer import Consumer
from tools.poc_file_ack.enqueue import atomic_write_cmd


def test_consumer_skips_file_missing_between_list_and_open(tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    d = str(tmp_path)

    bad = 'missing-1'
    good = 'good-1'

    atomic_write_cmd(d, {'id': bad, 'type': 'set_regulator', 'value': 0.1})
    atomic_write_cmd(d, {'id': good, 'type': 'set_regulator', 'value': 0.2})

    orig_open = builtins.open

    def fake_open(path, *args, **kwargs):
        if str(path).endswith(f'cmd-{bad}.json'):
            raise FileNotFoundError('simulated race: file removed after listing')
        return orig_open(path, *args, **kwargs)

    builtins.open = fake_open

    try:
        c = Consumer(d, poll_interval=0.01, process_time=0.01)
        c.start()
        time.sleep(0.2)
        c.stop()
        c.join(timeout=1)

        # good ack should exist
        ack_good = tmp_path / f'ack-{good}.json'
        assert ack_good.exists(), 'good command should have been processed'

        # logs should contain debug about skipping the missing file
        msgs = [r.getMessage() for r in caplog.records]
        assert any('Skipping file' in m and 'due to read/parse error' in m for m in msgs), msgs
    finally:
        builtins.open = orig_open
