import json
import logging
import os
import threading
import time
from collections import OrderedDict
from typing import Any, cast

logger = logging.getLogger(__name__)


class _OrderedSetDict(OrderedDict):
    """OrderedDict compatible wrapper that provides a set-like `add()` method.

    Tests expect a `processed` attribute that supports `.add(id)` but the
    implementation prefers an OrderedDict to maintain insertion order and
    timestamps. This small subclass preserves OrderedDict behaviour while
    adding an `add()` convenience method used in tests.

    NOTE: Historically `add(key, value=None)` treated *omitted* `value` the
    same as explicit `None` and stored the current timestamp. To make the
    API deterministic we use a sentinel default to distinguish omitted
    parameters from `None` explicitly passed by the caller.
    """

    _UNSET = object()

    def add(self, key, value=_UNSET):
        """Add key with an associated value.

        - If `value` is not provided, store the current timestamp (int(time.time())).
        - If `value` is provided and is `None`, store `None` explicitly.
        """
        if value is self._UNSET:
            # Value omitted: preserve previous behavior of recording a timestamp
            self[key] = int(time.time())
        else:
            # Explicit value given (including None): store it as-is
            self[key] = value


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
        # Declare _stop attribute (may be shadowed historically) so static checkers know it exists
        self._stop: Any | None = None
        # Use OrderedDict-like structure (with .add() compatibility) as an LRU-like structure: keys are cmd_ids, values are timestamps
        self.processed = _OrderedSetDict()
        self.processed_ids_file = os.path.join(self.dirpath, processed_ids_file)
        # Defensive: make sure we are not accidentally shadowing Thread._stop
        # Older versions of the class used `self._stop = threading.Event()` which
        # overwrote Thread._stop leading to TypeError in join() (Event not callable).
        if hasattr(self, '_stop') and not callable(self._stop):
            logger.warning("Consumer instance unexpectedly has non-callable '_stop' attribute; renaming to '_stop_shadow' to avoid join errors")
            # safe to access directly because hasattr guarded above
            self._stop_shadow = self._stop
            try:
                delattr(self, '_stop')
            except Exception:
                logger.exception("Failed to remove shadowing '_stop' attribute")
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
                with open(self.processed_ids_file, encoding='utf-8') as f:
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

    def join(self, timeout: float | None = None) -> None:
        """Override Thread.join to defensively remove any non-callable `_stop` attribute
        that may have been set on the instance (e.g., older code or external actors setting
        `self._stop = threading.Event()`). This prevents Thread.join from calling a
        non-callable attribute and raising a TypeError.
        """
        # If an instance attribute `_stop` exists and is not callable, remove it so the
        # class method `_stop` is used by the underlying Thread implementation.
        try:
            if hasattr(self, '_stop') and not callable(self._stop):
                logger.warning("Consumer.join found non-callable '_stop' attribute; removing to avoid join error")
                try:
                    delattr(self, '_stop')
                except Exception:
                    # Best-effort: log and continue to attempt to join
                    logger.exception("Failed to remove shadowing '_stop' attribute during join")
        except Exception:
            # Be extremely defensive: don't let introspection issues prevent joining
            logger.exception("Unexpected error while defensively checking '_stop' in join")
        # Delegate to Thread.join
        try:
            return super().join(timeout)
        except TypeError as e:
            # Defensive: in some CI environments a non-callable `_stop` may still be
            # present (e.g., as a class attribute) leading to Thread.join calling
            # a non-callable and raising TypeError. Attempt to repair the attribute
            # by setting a bound method to the instance and retrying once.
            logger.warning("Thread.join raised TypeError (likely due to non-callable _stop); attempting to repair and retry: %s", e)
            try:
                # remove instance attribute if present
                if hasattr(self, '_stop') and not callable(self._stop):
                    try:
                        delattr(self, '_stop')
                    except Exception:
                        logger.exception("Failed to delete instance '_stop' during join recovery")
                # if class attribute is non-callable, bind threading.Thread._stop to instance
                # Use vars(type(self)) to access class dict safely (avoids attribute access warnings)
                cls_vars = vars(type(self))
                cls_stop = cls_vars.get('_stop', None)

                cls_stop = cast(Any, cls_stop)
                if cls_stop is not None and not callable(cls_stop):
                    try:
                        stop_func = getattr(threading.Thread, '_stop', None)  # type: ignore[attr-defined]
                        if stop_func is not None:
                            bound = stop_func.__get__(self, threading.Thread)
                            self._stop = bound
                    except Exception:
                        logger.exception("Failed to bind Thread._stop to instance during join recovery")
                # As a final attempt, ensure instance has a callable _stop attribute
                if not callable(getattr(self, '_stop', None)):
                    try:
                        # Access the class attribute safely via getattr to avoid static checker
                        # complaints when `_stop` is not a known attribute on Thread.
                        cls_thread_stop = getattr(threading.Thread, '_stop', None)  # type: ignore[attr-defined]
                        if cls_thread_stop is not None:
                            self._stop = cast(Any, cls_thread_stop).__get__(self, threading.Thread)
                    except Exception:
                        logger.exception("Failed to set fallback _stop bound method on instance")
                # Retry join
                return super().join(timeout)
            except Exception:
                logger.exception("Retrying join failed; proceeding to raise the original TypeError")
                raise

    def run(self):
        while not self._stop_event.is_set():
            try:
                # ensure directory exists; if it was removed externally, attempt to recreate
                if not os.path.isdir(self.dirpath):
                    logger.warning("Consumer directory %s missing; recreating", self.dirpath)
                    try:
                        os.makedirs(self.dirpath, exist_ok=True)
                    except Exception:
                        logger.exception("Failed to recreate consumer directory %s; will retry", self.dirpath)
                        time.sleep(self.poll_interval)
                        continue
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
                            with open(path, encoding='utf-8') as fh:
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
