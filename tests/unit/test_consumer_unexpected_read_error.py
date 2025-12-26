import builtins
import logging
import time

from tools.poc_file_ack.consumer import Consumer
from tools.poc_file_ack.enqueue import atomic_write_cmd


def test_consumer_logs_unexpected_read_error_and_continues(tmp_path, caplog):
    caplog.set_level(logging.ERROR)
    d = str(tmp_path)

    cmd_id = 'badread-1'
    atomic_write_cmd(d, {'id': cmd_id, 'type': 'set_regulator', 'value': 0.2})

    # monkeypatch builtins.open to raise an unexpected error when opening this file
    orig_open = builtins.open

    def fake_open(path, *args, **kwargs):
        if str(path).endswith(f'cmd-{cmd_id}.json'):
            raise RuntimeError('unexpected')
        return orig_open(path, *args, **kwargs)

    builtins.open = fake_open

    try:
        c = Consumer(d, poll_interval=0.01, process_time=0)
        c.start()
        # allow a short time for the consumer to hit the error
        time.sleep(0.1)
        c.stop()
        c.join(timeout=1)

        messages = [r.getMessage() for r in caplog.records]
        assert any('Unexpected error reading command file' in m for m in messages), messages
    finally:
        builtins.open = orig_open
