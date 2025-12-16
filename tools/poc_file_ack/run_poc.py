import os
import time
from enqueue import atomic_write_cmd, wait_for_ack
from consumer import Consumer


def demo():
    d = os.path.abspath('./tmp_poc_dir')
    c = Consumer(d)
    c.start()
    try:
        cmd_id = atomic_write_cmd(d, {'type': 'set_regulator', 'value': 0.6})
        print('Wrote cmd', cmd_id)
        ack = wait_for_ack(d, cmd_id, timeout=5.0)
        print('ACK received:', ack)
    finally:
        c.stop()
        c.join()


if __name__ == '__main__':
    demo()
