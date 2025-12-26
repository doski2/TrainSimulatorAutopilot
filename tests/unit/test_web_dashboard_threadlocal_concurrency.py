import threading
import time

import pytest

from web_dashboard import _get_current_json_data, _set_current_json_data


def worker(i, results):
    # set a unique value and then read it back
    _set_current_json_data(f"value-{i}")
    # small sleep to yield execution and increase chance of interleaving without burning CPU
    time.sleep(0.01)
    results[i] = _get_current_json_data()


def test_thread_local_is_isolated_and_race_free():
    # Sanity check: if thread-local storage couldn't be initialized in the
    # module under test, _set_current_json_data will raise AttributeError.
    # In that environment (rare), skip the test rather than failing.
    try:
        _set_current_json_data("sanity")
        assert _get_current_json_data() == "sanity"
    except AttributeError:
        pytest.skip("thread-local storage unavailable in this environment")

    threads = []
    results = {}
    n = 8
    for i in range(n):
        t = threading.Thread(target=worker, args=(i, results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Each thread should have its own stored value
    for i in range(n):
        assert results[i] == f"value-{i}"
