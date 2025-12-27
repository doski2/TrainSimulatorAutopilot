# PoC File+ACK — Deprecated and moved

This directory is the canonical archive of the PoC for the "file + ACK" flow.
It was copied to `tools/deprecated/poc_file_ack` and the original package `tools/poc_file_ack` now contains shims that re-export the implementation while emitting a `DeprecationWarning`.

Reason for deprecation:
- The ACK-based flow was not reliable in real environments: the Lua plugin sometimes did not load, and Windows file I/O could fail due to `Access denied` / `file locked`.
- Keeping the ACK dependency made the API fragile (blocked requests and 504s in production-like setups).

If you need to re-enable the POC for experiments, use the copy under `tools/deprecated/poc_file_ack` and update tests/E2E accordingly. Prefer moving the PoC to its own branch if you plan to reintroduce ACK-based flows in the future.