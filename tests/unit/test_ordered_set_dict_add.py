import time

_SENTINEL = object()

class _OrderedSetDict(dict):
    def add(self, key, value=_SENTINEL):
        if value is _SENTINEL:
            value = int(time.time())
        self[key] = value


def test_add_without_value_stores_timestamp():
    s = _OrderedSetDict()
    s.add('a')
    assert 'a' in s
    # stored value should be int timestamp and recent
    val = s['a']
    assert isinstance(val, int)
    assert abs(val - int(time.time())) <= 2


def test_add_with_explicit_none_stores_none():
    s = _OrderedSetDict()
    s.add('b', None)
    assert 'b' in s
    assert s['b'] is None


def test_add_with_explicit_value_stores_value():
    s = _OrderedSetDict()
    s.add('c', 123)
    assert s['c'] == 123
