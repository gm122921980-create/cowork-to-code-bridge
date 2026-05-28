# Architecture

## Why a file-based bridge

Cowork sessions run in a sandbox. From inside Cowork you cannot:

- Open sockets to your Mac shell
- Launch processes outside the sandbox
- Read files outside the bind-mounted project directory
- Use your SSH keys, gh auth, Docker daemon, or `~/.claude.json`

What you *can* do: read and write files in the bind-mount.

The bridge exploits this. A small daemon on your Mac watches a directory for command files written by Cowork. It runs the requested script and writes the result back to a sibling directory. Cowork polls for the result file. Done.

## Components

| Component | Where it runs | Process model |
|---|---|---|
| Daemon (`daemon.py`) | Mac, started by launchd | Long-lived, polls every 1s |
| Client (`client.py`) | Cowork sandbox | Per-call: write JSON, poll for result |
| Whitelisted scripts | `~/.cowork-to-code-bridge/scripts/` on Mac | Spawned per command |

## File layout

```
~/.cowork-to-code-bridge/      ← BRIDGE_ROOT on Mac
├── .env                       ← BRIDGE_TOKEN, chmod 600
├── queue/                     ← Cowork writes here
│   └── 1716937200_abc123.json
├── results/                   ← daemon writes here
│   └── 1716937200_abc123.json
├── processed/                 ← daemon archives completed commands
│   └── 1716937200_abc123.json
├── scripts/                   ← whitelisted executables
│   ├── ping.sh
│   ├── hello.sh
│   └── your_script.sh
├── daemon.log                 ← stdout
└── daemon.err                 ← stderr
```

When `BRIDGE_ROOT` lives at a path visible to both the Mac and the Cowork bind-mount, this just works. The conventional placement is the user's home directory; Cowork's bind-mount can expose it via a symlink in the project root.

## Command lifecycle

1. **Client (Cowork)** generates `cmd_id = "<unix_ts>_<8hexdig>"`, builds the payload, writes to `queue/<cmd_id>.json.tmp`, renames to `.json` (atomic).
2. **Daemon (Mac)** sees the new file on its next poll, validates token + script path + args.
3. **Daemon** spawns the script with `subprocess.run`, captures stdout/stderr/exit, enforces timeout.
4. **Daemon** writes `results/<cmd_id>.json` atomically (`.tmp` rename).
5. **Daemon** moves `queue/<cmd_id>.json` → `processed/<cmd_id>.json` so it isn't re-run.
6. **Client** polling sees the result file appear, deserializes, returns dict to caller.

## Result schema

```json
{
  "id": "1716937200_abc123",
  "exit_code": 0,
  "stdout": "...",
  "stderr": "...",
  "ts_completed": 1716937201.234,
  "error": "(optional, only on daemon-side failure)"
}
```

Exit code conventions:

| Code | Meaning |
|---|---|
| `0`+ | Script's own exit code |
| `-1` | Daemon refused the command (bad token, bad path, missing script) |
| `-2` | Script ran but exceeded timeout |
| `-3` | Internal daemon error (subprocess crash, etc.) |

## Atomicity

Both sides use the `write-tmp + rename` pattern. The daemon only acts on `*.json` (not `*.json.tmp`), so it never reads a partial write. Same for results read by the client.

## Concurrency

The daemon processes queue files in lexicographic order (which, with `<unix_ts>_<rand>` IDs, is roughly submission order). Currently single-threaded — one script at a time. For most ops workloads this is fine; the bottleneck is usually the script itself, not the daemon dispatch.

For higher throughput, the daemon could fork per-command. Not in v0.1.0.

## Failure modes

| Failure | Symptom | Recovery |
|---|---|---|
| Daemon crashed | `call_remote` raises `TimeoutError` | launchd auto-restarts; check `daemon.err` |
| Bind-mount path changed | Client can't find `queue/` | Set `BRIDGE_ROOT` env var explicitly |
| Token mismatch | Result has `exit_code: -1, error: "bridge token mismatch"` | Re-read token from `.env`; restart Cowork session |
| Script missing | Result has `exit_code: -1, error: "script does not exist"` | Add script to `~/.cowork-to-code-bridge/scripts/` and `chmod +x` |
| Disk full | Daemon stops writing results | Free space; processed/ can be cleared safely |

## Comparison to alternatives

| Approach | Pros | Cons |
|---|---|---|
| **This bridge** | No network, no listener, survives Cowork sandbox limits | Polling latency (~1s), only works when bind-mount is shared |
| SSH from Cowork | Familiar | Cowork can't open sockets; no key material in sandbox |
| MCP server on Mac | Structured tool definitions | Cowork can't easily reach localhost services |
| Native Anthropic IPC | Would be ideal | Doesn't exist yet (as of v0.1.0) |
| Webhook + ngrok | Works | Heavy setup; exposes Mac to internet |
