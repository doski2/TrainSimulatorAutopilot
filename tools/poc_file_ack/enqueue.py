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


def send_command_with_retries(dirpath, payload, timeout=5.0, retries=3, initial_delay=0.5, backoff=2.0, poll=0.1):
    """Send a command and wait for ACK with retries and exponential backoff.

    Returns the ACK dict if received, otherwise None after exhausting retries.
    """
    # Ensure payload has an id so retries reuse same id (idempotent)
    cmd_id = payload.get('id') or str(uuid.uuid4())
    payload['id'] = cmd_id

    attempt = 0
    delay = initial_delay
    while attempt <= retries:
        # write (or rewrite) the command atomically
        tmp = os.path.join(dirpath, f"cmd-{cmd_id}.tmp")
        final = os.path.join(dirpath, f"cmd-{cmd_id}.json")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        os.replace(tmp, final)

        # wait for ack
        ack = wait_for_ack(dirpath, cmd_id, timeout=timeout, poll=poll)
        if ack is not None:
            return ack

        # not acked: decide to retry
        attempt += 1
        if attempt > retries:
            break
        time.sleep(delay)
        delay *= backoff

    return None


if __name__ == "__main__":
    # demo usage
    d = os.path.abspath("./tmp_poc_dir")
    print("Sending cmd to", d)
    ack = send_command_with_retries(d, {"type": "set_regulator", "value": 0.5}, timeout=2.0, retries=3, initial_delay=0.5)
    print("ACK:", ack)