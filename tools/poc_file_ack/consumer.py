import json
import os
import time
import threading


class Consumer(threading.Thread):
    """Simple consumer that polls a directory for cmd-*.json files
    and writes ack-{id}.json after 'processing'."""

    def __init__(self, dirpath, poll_interval=0.1, process_time=0.05):
        super().__init__(daemon=True)
        self.dirpath = dirpath
        self.poll_interval = poll_interval
        self.process_time = process_time
        self._stop = threading.Event()
        self.processed = set()
        os.makedirs(self.dirpath, exist_ok=True)
        # write a probe file to indicate the consumer/plugin is loaded
        self.write_probe_file()

    def write_probe_file(self):
        """Write a probe file 'plugin_loaded.txt' atomically to indicate readiness."""
        try:
            probe_path = os.path.join(self.dirpath, 'plugin_loaded.txt')
            tmp = probe_path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write('loaded: ' + str(int(time.time())) + '\n')
            os.replace(tmp, probe_path)
        except Exception:
            # best effort; don't raise to keep consumer alive
            pass

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
                    # mark processed and remove the command file
                    self.processed.add(cmd_id)
                    try:
                        os.remove(path)
                    except Exception:
                        pass
            except Exception:
                # swallow exceptions to keep consumer alive
                pass
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