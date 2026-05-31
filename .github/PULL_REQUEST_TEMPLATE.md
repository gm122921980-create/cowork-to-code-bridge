<!-- Thanks for contributing! Keep it focused; small PRs merge faster. -->

## What & why
<!-- What does this change, and why? Link any issue: Fixes #123 -->

## How I verified
<!-- Commands you ran. The suite must stay green. -->
- [ ] `pytest -q` passes
- [ ] `ruff check .` clean
- [ ] `bash -n install.sh` (if you touched shell)

## Checklist
- [ ] Kept the daemon/client dependency-free (stdlib only)
- [ ] Didn't change the script-whitelist / token / no-listener safety model
- [ ] If I changed the client API, updated all copies (`cowork_to_code_bridge/client.py`, `bridge_client.py`, `skill/.../bridge_client.py`) — the sync guard test passes
- [ ] Updated CHANGELOG.md if user-facing
