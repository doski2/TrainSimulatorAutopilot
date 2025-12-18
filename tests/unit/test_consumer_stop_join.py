import time

from tools.poc_file_ack.consumer import Consumer


def test_consumer_stop_and_join_does_not_raise(tmp_path):
    d = str(tmp_path)
    c = Consumer(d, poll_interval=0.01, process_time=0.01)
    c.start()
    time.sleep(0.05)
    c.stop()
    # should not raise
    c.join(timeout=1)
    assert not c.is_alive()
