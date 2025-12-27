import pytest
pytest.skip("ACK PoC deprecated — skipping consumer tests.", allow_module_level=True)

import json
import logging
import time

from tools.poc_file_ack.consumer import Consumer


def test_consumer_logs_unhandled_exception_and_continues(tmp_path, caplog):
    caplog.set_level(logging.ERROR)
    # create a command file that will trigger processing
    cmd = {'id': 'test1', 'type': 'start_autopilot'}
    cmd_path = tmp_path / 'cmd-test1.json'
    with open(cmd_path, 'w', encoding='utf-8') as f:
        json.dump(cmd, f)

    c = Consumer(str(tmp_path), poll_interval=0.01, process_time=0)
    original_persist = c._persist_processed_ids

    calls = {'n': 0}

    def bad_persist():
        calls['n'] += 1
        if calls['n'] == 1:
            # raise once to simulate an unexpected error during persistence
            raise RuntimeError('boom')
        # delegate to the original implementation thereafter
        return original_persist()

    c._persist_processed_ids = bad_persist

    c.start()
    # give the consumer a short moment to run and hit the bad_persist
    time.sleep(0.1)
    c.stop()
    c.join(timeout=1)

    # Ensure the thread stopped/joined
    assert not c.is_alive()

    # Check logs for either the persistence failure or the outer handler message
    messages = [r.getMessage() for r in caplog.records]
    assert any('Failed to persist' in m or 'Unhandled exception' in m or 'boom' in m for m in messages)
