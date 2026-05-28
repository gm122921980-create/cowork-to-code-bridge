# Cowork-side usage examples

After the Mac daemon is installed and the plugin is loaded:

## Health check

```python
from cowork_to_code_bridge import daemon_alive
assert daemon_alive(), "Daemon not responding — check launchctl on Mac"
```

## Run a script with args

```python
from cowork_to_code_bridge import call_remote

r = call_remote(
    script="scripts/git_status.sh",
    args=["/Users/me/myrepo"],
    timeout=30,
)
print(f"exit={r['exit_code']}")
print(r["stdout"])
```

## Run with extra environment

```python
r = call_remote(
    script="scripts/deploy.sh",
    args=["staging"],
    env={"DEPLOY_TOKEN": "..."},
    timeout=300,
)
```

## Override bridge location

By default the client looks in `$BRIDGE_ROOT` then `./bridge`. If your Cowork bind-mount lives elsewhere:

```python
r = call_remote(
    "scripts/ping.sh",
    bridge_root="/sessions/abc123/mnt/myproject/bridge",
)
```

Or set once for the session:

```python
import os
os.environ["BRIDGE_ROOT"] = "/sessions/abc123/mnt/myproject/bridge"
```
