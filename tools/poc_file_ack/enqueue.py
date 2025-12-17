import json
import os
import time
import uuid

# Defaults for wait_for_ack behavior
DEFAULT_ACK_TIMEOUT = 5.0
DEFAULT_ACK_POLL = 0.1


def atomic_write_cmd(dirpath, payload):
    """Write a command atomically as cmd-{id}.json and return the id.

    Note: make a shallow copy of the payload to avoid mutating the caller's
    dictionary (we add an `id` field for internal tracking).
    """
    os.makedirs(dirpath, exist_ok=True)
    # copy payload to avoid mutating caller's dict
    p = dict(payload)
    cmd_id = p.get("id") or str(uuid.uuid4())
    p["id"] = cmd_id
    tmp = os.path.join(dirpath, f"cmd-{cmd_id}.tmp")
    final = os.path.join(dirpath, f"cmd-{cmd_id}.json")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")
    # Atomic replace
    os.replace(tmp, final)
    return cmd_id


def wait_for_ack(dirpath, cmd_id, timeout: float = DEFAULT_ACK_TIMEOUT, poll: float = DEFAULT_ACK_POLL):
    """Wait for an ACK file for a given command id in `dirpath`.

    Parameters:
        dirpath (str): Directory where ack files are written.
        cmd_id (str): Command id to look for (ack-{cmd_id}.json).
        timeout (float): Maximum number of seconds to wait for the ack. Defaults
            to DEFAULT_ACK_TIMEOUT (5.0 seconds).
        poll (float): Interval in seconds between checks for the ack file.
            Defaults to DEFAULT_ACK_POLL (0.1 seconds).

    Returns:
        dict or None: Parsed JSON content of the ack file if found within
        timeout, otherwise None.
    """
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


import argparse
import tempfile
import logging

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Demo send command with retries')
    parser.add_argument('--dir', '-d', help='Directory to use for POC (default: temporary dir)')
    args = parser.parse_args()

    temp_ctx = None
    if args.dir:
        d = os.path.abspath(args.dir)
        os.makedirs(d, exist_ok=True)
        logger.info("Using provided directory for demo: %s", d)
    else:
        temp_ctx = tempfile.TemporaryDirectory(prefix='poc_')
        d = temp_ctx.name
        logger.info("Using temporary directory for demo: %s", d)

    print("Sending cmd to", d)
    ack = send_command_with_retries(d, {"type": "set_regulator", "value": 0.5}, timeout=2.0, retries=3, initial_delay=0.5)
    print("ACK:", ack)

    if temp_ctx is not None:
        temp_ctx.cleanup()
        logger.info("Temporary directory cleaned up: %s", d)