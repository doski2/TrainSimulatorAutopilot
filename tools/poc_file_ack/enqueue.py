import json
import os
import time
import uuid


def atomic_write_cmd(dirpath, payload):
    """Write a command atomically as cmd-{id}.json and return the id."""
    os.makedirs(dirpath, exist_ok=True)
    cmd_id = payload.get("id") or str(uuid.uuid4())
    payload["id"] = cmd_id
    tmp = os.path.join(dirpath, f"cmd-{cmd_id}.tmp")
    final = os.path.join(dirpath, f"cmd-{cmd_id}.json")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    # Atomic replace
    os.replace(tmp, final)
    return cmd_id


def wait_for_ack(dirpath, cmd_id, timeout=5.0, poll=0.1):
    ack = os.path.join(dirpath, f"ack-{cmd_id}.json")
    end = time.time() + timeout
    while time.time() < end:
        if os.path.exists(ack):
            with open(ack, "r", encoding="utf-8") as f:
                return json.load(f)
        time.sleep(poll)
    return None


if __name__ == "__main__":
    # demo usage
    d = os.path.abspath("./tmp_poc_dir")
    print("Writing cmd to", d)
    cmd_id = atomic_write_cmd(d, {"type": "set_regulator", "value": 0.5})
    print("Wrote cmd", cmd_id)
    ack = wait_for_ack(d, cmd_id, timeout=10.0)
    print("Received ack:", ack)