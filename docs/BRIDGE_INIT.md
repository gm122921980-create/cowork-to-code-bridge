# Bridge Initialization — Knowledge Base for First-Time Users

This is what a Cowork session needs to know the first time it connects to the
bridge. Read it once, then get to work. The same content is available
programmatically via `get_bridge_context()` (see
[`cowork_to_code_bridge/bridge_init.py`](../cowork_to_code_bridge/bridge_init.py))
so it travels with the package even when this file isn't mounted into the sandbox.

---

## 1. What the bridge is

You are a **Cowork session**. The bridge connects you to **Claude Code running on
the user's own machine** (macOS or Linux) through a small file-based daemon. Tasks
that need the real computer run *there*; results come back *here*.

There is no network call from your side. Everything moves through a shared
bind-mounted directory (`BRIDGE_ROOT`) containing `queue/`, `results/`, and
`to_cowork/`. The bridge is **idempotent** and **survives reboots**.

### Capabilities
| You can…                         | Examples                                  |
|----------------------------------|-------------------------------------------|
| Run scripts / commands           | any whitelisted script on the machine     |
| Build / run / test apps          | `npm run build`, `pytest`, app launch     |
| Use git against local repos      | push, pull, status, rebase                |
| Install packages                 | npm, pip, brew, docker                     |
| Inspect machine health           | RAM, disk, processes                       |
| Pass messages both ways          | Cowork ↔ Claude Code                       |

---

## 2. First-connection flow

```python
from cowork_to_code_bridge.bridge_init import (
    is_first_connection, get_bridge_context,
    get_initialization_message, mark_bridge_initialized,
)

if is_first_connection():
    print(get_initialization_message())  # friendly intro for the user
    print(get_bridge_context())          # load capabilities into context
    mark_bridge_initialized()            # remember — shown once per machine
```

- `is_first_connection()` — `True` until the machine is initialized. Pure read.
- `get_bridge_context()` — the full reference (this document, inlined). Pure.
- `get_initialization_message()` — short user-facing intro. Pure.
- `mark_bridge_initialized()` — drops a `.bridge_initialized` marker in
  `BRIDGE_ROOT`. **Idempotent**: safe to call repeatedly; the original timestamp
  is preserved. The write is atomic.

The marker lives in the ephemeral bridge state directory (gitignored) — never in
the repo — so it's per-machine, not per-clone.

---

## 3. Function reference

### `call_remote(script, args=None, timeout=60, ...)` — **blocking**
Run a script and wait for it. Returns `{exit_code, stdout, stderr, ...}`. Use when
you need the answer now and the work fits inside your sandbox timeout.

### `queue_task(script, args=None, timeout=60, idempotency_key=None, ...)` — **non-blocking**
Queue a task and return immediately: `{task_id, status:"queued", timestamp}`. Use
for long-running work or short sandbox timeouts. Pair with `poll_task_result`.

### `poll_task_result(task_id)` — **non-blocking, idempotent**
Check on a queued task. `status` ∈ `{"queued", "running", "completed", "unknown"}`;
on `"completed"` the dict also carries the full result. Safe to call repeatedly.

### `post_message_to_cowork(message_type, content, parent_task_id=None)`
Machine side → Cowork. `message_type` ∈ `{"progress","completed","error","info"}`.
Returns a `request_id`.

### `detect_messages_from_claude_code(parent_task_id=None)` — **idempotent**
Read messages Claude Code posted back. Optional `parent_task_id` filter. Returns a
list (empty if none). Safe to poll.

---

## 4. When to use each

| Goal                                 | Use                                |
|--------------------------------------|------------------------------------|
| Quick command, need result now       | `call_remote`                      |
| Long build/test, or short timeout    | `queue_task` + `poll_task_result`  |
| Avoid duplicate runs on retry        | `queue_task(idempotency_key=...)`  |
| Machine reports progress to Cowork    | `post_message_to_cowork`           |
| Cowork reads machine updates          | `detect_messages_from_claude_code` |

---

## 5. Async vs blocking

| | Blocking (`call_remote`) | Async (`queue_task` → `poll_task_result`) |
|---|---|---|
| Calls | one call, one result | queue, return, poll later |
| Best for | quick commands | slow / uncertain work |
| Risk | dies if work outlives sandbox timeout | none — task runs on the machine regardless |

**Rule of thumb: if it might take longer than ~30s, queue it.**

---

## 6. Idempotency guarantees

- `poll_task_result` and `detect_messages_from_claude_code` are **pure reads** —
  call as often as you like.
- `queue_task(idempotency_key=...)` won't double-execute the same logical task on
  retry.
- `is_first_connection()` only reads; `mark_bridge_initialized()` is safe to call
  repeatedly and preserves the original timestamp.

---

## 7. Common usage patterns

**Blocking — run tests:**
```python
from cowork_to_code_bridge import call_remote
r = call_remote("scripts/run_tests.sh", timeout=120)
print(r["exit_code"], r["stdout"])
```

**Async — long build, poll later:**
```python
from cowork_to_code_bridge.client import queue_task, poll_task_result
job = queue_task("scripts/build.sh", timeout=1800,
                 idempotency_key="build-main-2026-06-18")
# ... later turn ...
res = poll_task_result(job["task_id"])
if res["status"] == "completed":
    print(res["exit_code"], res["stdout"])
```

**Bidirectional — watch for progress from the machine:**
```python
from cowork_to_code_bridge.client import detect_messages_from_claude_code
for m in detect_messages_from_claude_code(parent_task_id=job["task_id"]):
    print(m["type"], m["content"])
```

---

## 8. Best practices

- Prefer **`queue_task`** for anything slow; never block your sandbox on a long job.
- Always pass an **`idempotency_key`** for state-changing work (deploys,
  migrations) so retries don't double-fire.
- **Poll, don't spin** — call `poll_task_result` on later turns, not in a tight loop.
- Use **`post_message_to_cowork`** from the machine side to stream progress instead
  of going silent during long jobs.
- Treat reads (`poll_*` / `detect_*`) as free and side-effect-free; treat
  `queue_*` / `call_*` as the only things that change state.
