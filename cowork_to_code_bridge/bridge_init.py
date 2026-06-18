"""
bridge_init.py — first-connection detection and initialization knowledge.

When a Cowork session connects to the bridge for the first time, it has no idea
what the bridge can do. This module hands it that knowledge — a compact, agnostic
description of the bridge's capabilities and the four functions that drive it —
and remembers (via a marker file) that the knowledge has been delivered, so the
context is offered exactly once per machine instead of on every reconnect.

Everything here is:
  - Agnostic:    no user/project-specific assumptions; reads BRIDGE_ROOT like the
                 rest of the client.
  - Idempotent:  is_first_connection() and mark_bridge_initialized() are safe to
                 call any number of times; the marker is written atomically.
  - Non-blocking: no network, no daemon round-trip, no polling — every call
                 returns immediately off the local filesystem.

Typical use (from a Cowork session, right after connecting):

    from cowork_to_code_bridge.bridge_init import (
        is_first_connection, get_bridge_context, mark_bridge_initialized,
        get_initialization_message,
    )

    if is_first_connection():
        print(get_initialization_message())   # show the user a friendly intro
        print(get_bridge_context())            # load capabilities into context
        mark_bridge_initialized()              # don't repeat next time
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

# Name of the marker file dropped in BRIDGE_ROOT once the context has been read.
# Lives in the ephemeral bridge state dir (gitignored), never in the repo.
MARKER_NAME = ".bridge_initialized"


def _resolve_bridge_root(bridge_root: Path | str | None = None) -> Path:
    """Find the bridge directory, matching client.py's resolution order.

    Order: explicit arg > $BRIDGE_ROOT > $PWD/bridge > package-relative fallback.
    Kept in sync with cowork_to_code_bridge.client._resolve_bridge_root so the
    marker lands next to queue/ and results/.
    """
    if bridge_root:
        return Path(bridge_root)
    env = os.environ.get("BRIDGE_ROOT")
    if env:
        return Path(env)
    cwd_bridge = Path.cwd() / "bridge"
    if cwd_bridge.exists():
        return cwd_bridge
    return Path(__file__).resolve().parents[2] / "bridge"


def get_bridge_context() -> str:
    """Return the full initialization knowledge base as a string.

    This is the same content as docs/BRIDGE_INIT.md, inlined so it travels with
    the package and is available even when the docs/ tree isn't mounted into the
    Cowork sandbox. Pure function — no side effects, returns immediately.

    Load this into a session's context on first connection so the agent knows
    what the bridge can do before it tries to use it.
    """
    return _BRIDGE_CONTEXT


def is_first_connection(bridge_root: Path | str | None = None) -> bool:
    """True if this machine has not yet been initialized (marker absent).

    Idempotent and non-blocking: only checks for the existence of the marker
    file in BRIDGE_ROOT. Never writes. Call freely.

    Args:
        bridge_root: Override the auto-detected bridge directory.
    """
    root = _resolve_bridge_root(bridge_root)
    return not (root / MARKER_NAME).exists()


def mark_bridge_initialized(bridge_root: Path | str | None = None) -> dict[str, Any]:
    """Create the .bridge_initialized marker so future connections skip the intro.

    Idempotent: if the marker already exists it is left untouched and its original
    timestamp is preserved. The write is atomic (write-temp-then-rename), so a
    crashed or concurrent call can never leave a half-written marker.

    Args:
        bridge_root: Override the auto-detected bridge directory.

    Returns:
        Dict with keys:
          initialized (bool)        always True after this returns
          already_initialized (bool) True if the marker existed before this call
          marker_path (str)         absolute path to the marker
          ts (float)                initialization timestamp (original if pre-existing)
    """
    root = _resolve_bridge_root(bridge_root)
    root.mkdir(parents=True, exist_ok=True)
    marker = root / MARKER_NAME

    if marker.exists():
        try:
            existing = json.loads(marker.read_text())
            ts = float(existing.get("ts", 0.0))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            ts = 0.0
        return {
            "initialized": True,
            "already_initialized": True,
            "marker_path": str(marker),
            "ts": ts,
        }

    ts = time.time()
    payload = {
        "initialized": True,
        "ts": ts,
        "version": _INIT_VERSION,
    }
    tmp = marker.with_suffix(marker.suffix + ".tmp")
    tmp.write_text(json.dumps(payload))
    tmp.rename(marker)

    return {
        "initialized": True,
        "already_initialized": False,
        "marker_path": str(marker),
        "ts": ts,
    }


def get_initialization_message() -> str:
    """Return a short, user-friendly message to show on the first connection.

    Plain text, safe to print directly to a Cowork chat. Pure function.
    """
    return _INIT_MESSAGE


# --------------------------------------------------------------------------- #
# Static content
# --------------------------------------------------------------------------- #

_INIT_VERSION = 1

_INIT_MESSAGE = """\
🌉  Bridge connected for the first time.

You're now talking to Claude Code running on the user's own machine. Anything
that needs the real computer — builds, tests, git, installs, system checks — can
run there and the results come back here.

Quick mental model:
  • call_remote(...)                 run something and wait for the result
  • queue_task(...) + poll_task_result(...)   fire-and-forget, then poll later
  • post_message_to_cowork(...)      Claude Code → Cowork updates
  • detect_messages_from_claude_code(...)   read those updates back

Run get_bridge_context() for the full reference, or read docs/BRIDGE_INIT.md.
This intro is shown once; later connections skip straight to work.
"""

_BRIDGE_CONTEXT = """\
# Bridge Capabilities — Initialization Context

You are a Cowork session connected to **Claude Code running on the user's own
machine** (macOS or Linux) through a small file-based bridge. Tasks that need the
real computer run there; results flow back to you.

## What the bridge can do
- Run any whitelisted script or command on the machine.
- Build / run / test real applications.
- git operations (push, pull, status) against local repos.
- Install packages (npm, pip, brew, docker, …).
- Inspect machine health (RAM, disk, processes).
- Pass messages both directions between Cowork and Claude Code.

The bridge is file-based and idempotent: it survives reboots and short sandbox
timeouts. There is no network call from your side — everything moves through a
shared bind-mounted directory (BRIDGE_ROOT) holding queue/, results/, and
to_cowork/.

## Function reference

### call_remote(script, args=None, timeout=60, ...)  — BLOCKING
Run a script on the machine and wait for it to finish. Returns a dict with
exit_code, stdout, stderr. Use when you need the answer right now and the work
fits inside your sandbox timeout.

### queue_task(script, args=None, timeout=60, idempotency_key=None, ...)  — NON-BLOCKING
Queue a task and return immediately with {task_id, status:"queued", timestamp}.
Use for long-running work, or whenever your sandbox has a short timeout (e.g.
~45s). Pair with poll_task_result.

### poll_task_result(task_id)  — NON-BLOCKING, IDEMPOTENT
Check on a queued task. Returns status one of: "queued", "running", "completed"
(with full result), or "unknown". Safe to call repeatedly — no side effects.

### post_message_to_cowork(message_type, content, parent_task_id=None)
Used by Claude Code (machine side) to push a structured update back to Cowork:
message_type ∈ {"progress","completed","error","info"}. Returns a request_id.

### detect_messages_from_claude_code(parent_task_id=None)  — IDEMPOTENT
Read messages Claude Code posted back. Optionally filter to one parent_task_id.
Returns a list (empty if none). Safe to poll.

## When to use each

| Goal                                   | Use                              |
|----------------------------------------|----------------------------------|
| Quick command, need result now         | call_remote                      |
| Long build/test, or short timeout      | queue_task + poll_task_result    |
| Avoid duplicate runs on retry          | queue_task(idempotency_key=...)  |
| Machine reports progress to Cowork     | post_message_to_cowork           |
| Cowork reads machine updates           | detect_messages_from_claude_code |

## Async vs blocking
- **Blocking (call_remote):** simplest; one call, one result. Risk: if the work
  outlives your sandbox timeout, the call dies even though the task may finish on
  the machine.
- **Async (queue_task → poll_task_result):** robust for anything slow or
  uncertain. Queue, return, poll on a later turn. The task keeps running on the
  machine regardless of your sandbox lifecycle.

Rule of thumb: if it might take longer than ~30s, queue it.

## Idempotency guarantees
- poll_task_result and detect_messages_from_claude_code are pure reads — call
  them as often as you like.
- queue_task with an idempotency_key won't double-execute the same logical task
  on retry.
- Initialization (this module) is marker-based: is_first_connection() only reads,
  mark_bridge_initialized() is safe to call repeatedly and preserves the original
  timestamp.

## Common usage patterns

Blocking — run tests and read the result:
    from cowork_to_code_bridge import call_remote
    r = call_remote("scripts/run_tests.sh", timeout=120)
    print(r["exit_code"], r["stdout"])

Async — long build, poll later:
    from cowork_to_code_bridge.client import queue_task, poll_task_result
    job = queue_task("scripts/build.sh", timeout=1800,
                     idempotency_key="build-main-2026-06-18")
    # ... later turn ...
    res = poll_task_result(job["task_id"])
    if res["status"] == "completed":
        print(res["exit_code"], res["stdout"])

Bidirectional — watch for progress from the machine:
    from cowork_to_code_bridge.client import detect_messages_from_claude_code
    for m in detect_messages_from_claude_code(parent_task_id=job["task_id"]):
        print(m["type"], m["content"])

## Best practices
- Prefer **queue_task** for anything slow; never block your sandbox on a long job.
- Always pass an **idempotency_key** for state-changing work (deploys, migrations)
  so retries don't double-fire.
- **Poll, don't spin:** call poll_task_result on later turns, not in a tight loop.
- Use **post_message_to_cowork** from the machine side to stream progress instead
  of going silent during long jobs.
- Treat reads (poll/detect) as free and side-effect-free; treat queue/call as the
  only things that change state.
"""
