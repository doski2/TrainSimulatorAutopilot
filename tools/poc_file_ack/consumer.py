import json
import os
import time
import threading
import logging

logger = logging.getLogger(__name__)


class Consumer(threading.Thread):
    """Simple consumer that polls a directory for cmd-*.json files
    and writes ack-{id}.json after 'processing'."""

    def __init__(self, dirpath, poll_interval=0.1, process_time=0.05, processed_ids_file='processed_ids.json'):
        super().__init__(daemon=True)
        self.dirpath = dirpath
        self.poll_interval = poll_interval
        self.process_time = process_time
        self._stop = threading.Event()
        self.processed = set()
        self.processed_ids_file = os.path.join(self.dirpath, processed_ids_file)
        os.makedirs(self.dirpath, exist_ok=True)
        # load persisted processed ids (if present)
        self._load_processed_ids()
        # write a probe file to indicate the consumer/plugin is loaded
        self.write_probe_file()

    def _load_processed_ids(self):
        try:
            if os.path.exists(self.processed_ids_file):
                with open(self.processed_ids_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.processed.update(data)
        except Exception:
            logger.exception("Failed to load processed_ids from %s", self.processed_ids_file)

    def _persist_processed_ids(self):
        """Persist the processed ids set to disk atomically."""
        try:
            tmp = self.processed_ids_file + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(list(self.processed), f, ensure_ascii=False)
            os.replace(tmp, self.processed_ids_file)
        except Exception:
            logger.exception("Failed to persist processed ids to %s", self.processed_ids_file)

    def write_probe_file(self):
        """Write a probe file 'plugin_loaded.txt' atomically to indicate readiness."""
        try:
            probe_path = os.path.join(self.dirpath, 'plugin_loaded.txt')
            tmp = probe_path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write('loaded: ' + str(int(time.time())) + '\n')
            os.replace(tmp, probe_path)
        except Exception:
            logger.exception("Failed to write probe file in %s", self.dirpath)
    def stop(self):
        self._stop.set()

    def run(self):
        while not self._stop.is_set():
            try:
                files = [f for f in os.listdir(self.dirpath) if f.startswith("cmd-") and f.endswith('.json')]
                for f in files:
                    path = os.path.join(self.dirpath, f)
                    try:
                        with open(path, 'r', encoding='utf-8') as fh:
                            payload = json.load(fh)
                    except Exception:
                        # file might be partial or deleted; skip
                        logger.debug("Skipping file %s due to read/parse error", path, exc_info=True)
                        continue
                    cmd_id = payload.get('id')
                    if not cmd_id or cmd_id in self.processed:
                        # remove/ignore duplicates
                        try:
                            os.remove(path)
                        except Exception:
                            pass
                        continue
                    # simulate processing
                    time.sleep(self.process_time)
                    # write ack
                    ack_path = os.path.join(self.dirpath, f"ack-{cmd_id}.json")
                    ack = {
                        'id': cmd_id,
                        'status': 'applied',
                        'ts': int(time.time()),
                        'notes': f"Processed {payload.get('type') or 'cmd'}"
                    }
                    with open(ack_path + '.tmp', 'w', encoding='utf-8') as af:
                        af.write(json.dumps(ack, ensure_ascii=False) + '\n')
                    os.replace(ack_path + '.tmp', ack_path)
                    # mark processed and persist
                    self.processed.add(cmd_id)
                    self._persist_processed_ids()
                    # remove the command file
                    try:
                        os.remove(path)
                    except Exception:
                        pass
            except KeyboardInterrupt:
                raise
            except Exception:
                logger.exception("Unhandled exception in Consumer run loop; continuing")
            time.sleep(self.poll_interval)


if __name__ == '__main__':
    d = os.path.abspath('./tmp_poc_dir')
    c = Consumer(d)
    c.start()
    print('Consumer started - polling', d)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        c.stop()
        c.join()
        print('Stopped')