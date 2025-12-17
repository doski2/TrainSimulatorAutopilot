import os
import time
import argparse
import tempfile
import logging
from tools.poc_file_ack.enqueue import atomic_write_cmd, wait_for_ack
from tools.poc_file_ack.consumer import Consumer

logger = logging.getLogger(__name__)


def demo(dirpath: str | None = None):
    """Run a short POC using dirpath if provided, otherwise a temporary dir."""
    # choose directory: given dir or a temporary directory
    temp_ctx = None
    if dirpath:
        d = os.path.abspath(dirpath)
        os.makedirs(d, exist_ok=True)
        logger.info("Using provided directory for POC: %s", d)
    else:
        temp_ctx = tempfile.TemporaryDirectory(prefix="poc_")
        d = temp_ctx.name
        logger.info("Using temporary directory for POC: %s", d)

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
        if temp_ctx is not None:
            temp_ctx.cleanup()
            logger.info("Temporary directory cleaned up: %s", d)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Run POC consumer + enqueue demo')
    parser.add_argument('--dir', '-d', help='Directory to use for POC (default: temporary directory)')
    args = parser.parse_args()
    demo(args.dir)
