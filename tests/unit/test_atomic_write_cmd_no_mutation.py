import os
import json
from tools.poc_file_ack.enqueue import atomic_write_cmd


def test_atomic_write_cmd_does_not_mutate_payload(tmp_path):
    d = str(tmp_path)
    payload = {'type': 'set_regulator', 'value': 0.9}
    original = dict(payload)  # keep a copy

    cmd_id = atomic_write_cmd(d, payload)

    # payload must remain unchanged
    assert payload == original

    # cmd file created and contains id
    cmd_file = os.path.join(d, f'cmd-{cmd_id}.json')
    assert os.path.exists(cmd_file)
    with open(cmd_file, 'r', encoding='utf-8') as f:
        content = json.load(f)
    assert content['id'] == cmd_id
    # original fields preserved in file
    assert content['type'] == original['type']
    assert content['value'] == original['value']
