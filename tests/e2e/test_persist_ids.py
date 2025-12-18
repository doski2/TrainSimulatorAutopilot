import os
import tempfile
import time

from tools.poc_file_ack.consumer import Consumer
from tools.poc_file_ack.enqueue import atomic_write_cmd


def test_persist_processed_ids_across_restarts():
    with tempfile.TemporaryDirectory() as d:
        # start consumer and process a command
        c1 = Consumer(d, poll_interval=0.01, process_time=0.01)
        c1.start()
        try:
            cmd_id = atomic_write_cmd(d, {"id": "persist-1", "type": "set_regulator", "value": 0.3})
            # wait for ack
            ack_path = os.path.join(d, f"ack-{cmd_id}.json")
            end = time.time() + 2.0
            while time.time() < end and not os.path.exists(ack_path):
                time.sleep(0.01)
            assert os.path.exists(ack_path)
        finally:
            c1.stop()
            c1.join()

        # processed_ids file should exist
        processed_file = os.path.join(d, "processed_ids.json")
        assert os.path.exists(processed_file)

        # start a new consumer; it should load the processed id and ignore re-submitted command
        c2 = Consumer(d, poll_interval=0.01, process_time=0.01)
        c2.start()
        try:
            # create the same command again
            atomic_write_cmd(d, {"id": "persist-1", "type": "set_regulator", "value": 0.3})
            # give some time for consumer to pick it up
            time.sleep(0.5)
            # since id was processed, consumer should remove the command and not produce a new ack with different timestamp
            # confirm that there is still only one ack file for that id
            # read ack content
            with open(ack_path, encoding="utf-8") as f:
                original_ack = f.read()
            # wait a bit and ensure content unchanged
            time.sleep(0.5)
            with open(ack_path, encoding="utf-8") as f:
                new_ack = f.read()
            assert original_ack == new_ack
        finally:
            c2.stop()
            c2.join()
