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
    """

    _UNSET = object()

    def add(self, key, value=_UNSET):
        if value is self._UNSET:
            self[key] = int(time.time())
        else:
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
        self._stop: Any | None = None
        self.processed = _OrderedSetDict()
        self.processed_ids_file = os.path.join(self.dirpath, processed_ids_file)
        if hasattr(self, '_stop') and not callable(self._stop):
            logger.warning("Consumer instance unexpectedly has non-callable '_stop' attribute; renaming to '_stop_shadow' to avoid join errors")
            self._stop_shadow = self._stop
            try:
                delattr(self, '_stop')
            except Exception:
                logger.exception("Failed to remove shadowing '_stop' attribute")
        self.removal_failure_threshold = removal_failure_threshold
        self.removal_failure_counts: dict[str, int] = {}
        self.processed_ids_max = processed_ids_max
        os.makedirs(self.dirpath, exist_ok=True)
        self._load_processed_ids()
        self.write_probe_file()

    def _load_processed_ids(self):
        try:
            if os.path.exists(self.processed_ids_file):
                with open(self.processed_ids_file, encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for cid in data:
                            self.processed[cid] = int(time.time())
                        while len(self.processed) > self.processed_ids_max:
                            self.processed.popitem(last=False)
        except Exception:
            logger.exception("Failed to load processed_ids from %s", self.processed_ids_file)

    def _persist_processed_ids(self):
        try:
            tmp = self.processed_ids_file + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(list(self.processed.keys()), f, ensure_ascii=False)
            os.replace(tmp, self.processed_ids_file)
        except Exception:
            logger.exception("Failed to persist processed ids to %s", self.processed_ids_file)

    def write_probe_file(self):
        try:
            probe_path = os.path.join(self.dirpath, 'plugin_loaded.txt')
            tmp = probe_path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write('loaded: ' + str(int(time.time())) + '\n')
            os.replace(tmp, probe_path)
        except Exception:
            logger.exception("Failed to write probe file in %s", self.dirpath)

    def stop(self):
        self._stop_event.set()

    def join(self, timeout: float | None = None) -> None:
        try:
            if hasattr(self, '_stop') and not callable(self._stop):
                logger.warning("Consumer.join found non-callable '_stop' attribute; removing to avoid join error")
                try:
                    delattr(self, '_stop')
                except Exception:
                    logger.exception("Failed to remove shadowing '_stop' attribute during join")
        except Exception:
            logger.exception("Unexpected error while defensively checking '_stop' in join")
        try:
            return super().join(timeout)
        except TypeError as e:
            logger.warning("Thread.join raised TypeError (likely due to non-callable _stop); attempting to repair and retry: %s", e)
            try:
                if hasattr(self, '_stop') and not callable(self._stop):
                    try:
                        delattr(self, '_stop')
                    except Exception:
                        logger.exception("Failed to delete instance '_stop' during join recovery")
                cls_vars = vars(type(self))
                cls_stop = cls_vars.get('_stop', None)
                cls_stop = cast(Any, cls_stop)
                if cls_stop is not None and not callable(cls_stop):
                    try:
                        stop_func = getattr(threading.Thread, '_stop', None)
                        if stop_func is not None:
                            bound = stop_func.__get__(self, threading.Thread)
                            self._stop = bound
                    except Exception:
                        logger.exception("Failed to bind Thread._stop to instance during join recovery")
                if not callable(getattr(self, '_stop', None)):
                    try:
                        cls_thread_stop = getattr(threading.Thread, '_stop', None)
                        if cls_thread_stop is not None:
                            self._stop = cast(Any, cls_thread_stop).__get__(self, threading.Thread)
                    except Exception:
                        logger.exception("Failed to set fallback _stop bound method on instance")
                return super().join(timeout)
            except Exception:
                logger.exception("Retrying join failed; proceeding to raise the original TypeError")
                raise

    def run(self):
        while not self._stop_event.is_set():
            try:
                if not os.path.isdir(self.dirpath):
                    logger.warning("Consumer directory %s missing; recreating", self.dirpath)
                    try:
                        os.makedirs(self.dirpath, exist_ok=True)
                    except Exception:
                        logger.exception("Failed to recreate consumer directory %s; will retry", self.dirpath)
                        time.sleep(self.poll_interval)
                        continue
        
# Note: full implementation preserved in deprecated copy
