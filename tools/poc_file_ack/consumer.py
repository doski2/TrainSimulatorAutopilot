import json
import os
import time
import threading
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)


class Consumer(threading.Thread):
    """Simple consumer that polls a directory for cmd-*.json files
    and writes ack-{id}.json after 'processing'.

    The consumer maintains a bounded LRU-like cache of processed ids to
    avoid unbounded memory growth on long-running processes. The maximum
    number of stored ids is configurable via `processed_ids_max`.
    """

    def __init__(self, dirpath, poll_interval=0.1, process_time=0.05, processed_ids_file='processed_ids.json', removal_failure_threshold: int = 5, processed_ids_max: int = 10000):
        super().__init__(daemon=True)
        self.dirpath = dirpath
        self.poll_interval = poll_interval
        self.process_time = process_time
        self._stop_event = threading.Event()
        # Use OrderedDict as an LRU-like structure: keys are cmd_ids, values are timestamps
        self.processed = OrderedDict()
        self.processed_ids_file = os.path.join(self.dirpath, processed_ids_file)
        # track repeated failures to remove files so we can alert if persistent
        self.removal_failure_threshold = removal_failure_threshold
        self.removal_failure_counts: dict[str, int] = {}
        # max number of processed ids to retain in memory/persistence
        self.processed_ids_max = processed_ids_max
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
                        # preserve order from file; values store timestamp
                        for cid in data:
                            self.processed[cid] = int(time.time())
                        # trim if persisted file is larger than allowed
                        while len(self.processed) > self.processed_ids_max:
                            self.processed.popitem(last=False)
        except Exception:
            logger.exception("Failed to load processed_ids from %s", self.processed_ids_file)

    def _persist_processed_ids(self):
        """Persist the processed ids set to disk atomically."""
        try:
            tmp = self.processed_ids_file + '.tmp'
            # write only the keys in insertion order (most recent at the end)
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(list(self.processed.keys()), f, ensure_ascii=False)
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
        """Signal the consumer to stop gracefully."""
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            try:
                # use scandir for better performance on directories with many files
                with os.scandir(self.dirpath) as it:
                    for entry in it:
                        try:
                            if not entry.is_file():
                                continue
                        except Exception:
                            # If entry disappears or is inaccessible, skip it
                            logger.debug("Skipping non-file entry in dir scan: %s", entry, exc_info=True)
                            continue
                        f = entry.name
                        if not (f.startswith("cmd-") and f.endswith('.json')):
                            continue
                        path = entry.path
                        try:
                            with open(path, 'r', encoding='utf-8') as fh:
                                payload = json.load(fh)
                        except json.JSONDecodeError as e:
                            # malformed JSON: remove file and log warning
                            logger.warning("Malformed command file %s; removing file. Error: %s", path, e)
                            try:
                                os.remove(path)
                                if path in self.removal_failure_counts:
                                    del self.removal_failure_counts[path]
                            except FileNotFoundError:
                                pass
                            except Exception:
                                cnt = self.removal_failure_counts.get(path, 0) + 1
                                self.removal_failure_counts[path] = cnt
                                logger.exception("Failed to remove malformed command file %s (attempt %d)", path, cnt)
                                if cnt >= self.removal_failure_threshold:
                                    logger.error("Persistent failure removing malformed command file %s after %d attempts", path, cnt)
                            continue
                        except (FileNotFoundError, PermissionError) as e:
                            # file might be partial or deleted or permission denied; skip with a debug log
                            logger.debug("Skipping file %s due to read/parse error: %s", path, e)
                            continue
                        except Exception:
                            # unexpected error reading file; log full exception to aid debugging
                            logger.exception("Unexpected error reading command file %s; skipping", path)
                            continue
                        cmd_id = payload.get('id')
                        if not cmd_id or cmd_id in self.processed:
                            # remove/ignore duplicates or malformed commands — log a warning to aid debugging
                            reason = 'missing id' if not cmd_id else 'duplicate id'
                            logger.warning("Ignoring command file %s (%s); removing file.", path, reason)
                            try:
                                os.remove(path)
                                # successful removal -> reset counter if any
                                if path in self.removal_failure_counts:
                                    del self.removal_failure_counts[path]
                            except FileNotFoundError:
                                # already removed by another actor; ignore
                                pass
                            except Exception:
                                # increment failure counter and alert if persistent
                                cnt = self.removal_failure_counts.get(path, 0) + 1
                                self.removal_failure_counts[path] = cnt
                                logger.exception("Failed to remove ignored command file %s (attempt %d)", path, cnt)
                                if cnt >= self.removal_failure_threshold:
                                    logger.error("Persistent failure removing ignored command file %s after %d attempts", path, cnt)
                            continue
                        # simulate processing
                        time.sleep(self.process_time)
                        # mark processed and persist BEFORE writing ack to avoid race conditions
                        # Use OrderedDict to maintain insertion order and support bounded size
                        self.processed[cmd_id] = int(time.time())
                        # evict oldest if we exceed configured maximum
                        if len(self.processed) > self.processed_ids_max:
                            evicted, _ = self.processed.popitem(last=False)
                            logger.info("Evicted old processed id %s to keep max=%d", evicted, self.processed_ids_max)
                        try:
                            self._persist_processed_ids()
                        except Exception:
                            # persistence failed; log and continue — processed is in-memory
                            logger.exception("Failed to persist processed id %s immediately after processing", cmd_id)
                        # write ack
                        ack_path = os.path.join(self.dirpath, f"ack-{cmd_id}.json")
                        ack = {
                            'id': cmd_id,
                            'status': 'applied',
                            'ts': int(time.time()),
                            'notes': f"Processed {payload.get('type') or 'cmd'}"
                        }
                        try:
                            with open(ack_path + '.tmp', 'w', encoding='utf-8') as af:
                                af.write(json.dumps(ack, ensure_ascii=False) + '\n')
                            os.replace(ack_path + '.tmp', ack_path)
                        except Exception:
                            logger.exception("Failed to write ack for %s", cmd_id)
                        # remove the command file
                        try:
                            os.remove(path)
                            if path in self.removal_failure_counts:
                                del self.removal_failure_counts[path]
                        except FileNotFoundError:
                            # already removed by another actor; ignore
                            pass
                        except Exception:
                            cnt = self.removal_failure_counts.get(path, 0) + 1
                            self.removal_failure_counts[path] = cnt
                            logger.exception("Failed to remove command file %s after processing %s (attempt %d)", path, cmd_id, cnt)
                            if cnt >= self.removal_failure_threshold:
                                logger.error("Persistent failure removing processed command file %s after %d attempts", path, cnt)
            except KeyboardInterrupt:
                raise
            except Exception:
                logger.exception("Unhandled exception in Consumer run loop; continuing")
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