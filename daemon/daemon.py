#!/usr/bin/env python3
"""
daemon.py — runs on the user's Mac. Polls bridge/queue/ for command files
written by Cowork (sandbox). Executes whitelisted scripts. Writes results to
bridge/results/.

Security:
  - Only scripts located under SCRIPTS_DIR (relative to BRIDGE_ROOT) are
    executable. No arbitrary shell.
  - Script names must match a strict regex (alphanumerics + `_`, `/`, `.`, `-`,
    ending in .sh or .py). No `..` traversal.
  - Token-authenticated: every command must include the BRIDGE_TOKEN matching
    the daemon's loaded token. Mismatch -> rejected.

Configuration (env vars or .env in BRIDGE_ROOT):
  BRIDGE_ROOT       Directory containing queue/, results/, processed/.
                    Default: ~/.cowork-to-code-bridge
  BRIDGE_SCRIPTS    Directory of whitelisted scripts.
                    Default: $BRIDGE_ROOT/scripts
  BRIDGE_TOKEN      Required shared secret. If unset, daemon refuses to start
                    unless BRIDGE_ALLOW_UNAUTH=1 (dev only — NEVER in prod).
  BRIDGE_POLL_SEC   Poll interval in seconds. Default: 1.0
  BRIDGE_MAX_TIMEOUT Max script timeout in seconds (caps user input). Default: 600

Start:
    cowork-to-code-bridge-daemon
    # or
    python3 -m cowork_to_code_bridge.daemon
"""
from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────
BRIDGE_ROOT = Path(os.environ.get("BRIDGE_ROOT", Path.home() / ".cowork-to-code-bridge")).expanduser()
SCRIPTS_DIR = Path(os.environ.get("BRIDGE_SCRIPTS", BRIDGE_ROOT / "scripts")).expanduser()
QUEUE = BRIDGE_ROOT / "queue"
RESULTS = BRIDGE_ROOT / "results"
PROCESSED = BRIDGE_ROOT / "processed"
POLL_SEC = float(os.environ.get("BRIDGE_POLL_SEC", "1.0"))
MAX_TIMEOUT_SEC = int(os.environ.get("BRIDGE_MAX_TIMEOUT", "600"))
ALLOW_UNAUTH = os.environ.get("BRIDGE_ALLOW_UNAUTH") == "1"

# Allow only relative paths inside scripts/, ending in .sh or .py.
SAFE_NAME = re.compile(r"^scripts/[A-Za-z0-9_/.-]+\.(sh|py)$")


def load_env() -> dict[str, str]:
    """Merge process env with .env in BRIDGE_ROOT (process env wins)."""
    env = dict(os.environ)
    env_file = BRIDGE_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env


def log(msg: str) -> None:
    print(f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] {msg}", flush=True)


def write_result(cmd_id: str, payload: dict) -> None:
    """Atomic-write a result file."""
    payload.setdefault("id", cmd_id)
    payload.setdefault("ts_completed", time.time())
    out = RESULTS / f"{cmd_id}.json"
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload))
    tmp.rename(out)


def run_one(cmd_path: Path, token_required: str | None) -> None:
    cmd_id = cmd_path.stem
    try:
        cmd = json.loads(cmd_path.read_text())
    except Exception as e:
        log(f"  ! bad json in {cmd_path.name}: {e}")
        cmd_path.unlink(missing_ok=True)
        return

    # ─── auth ─────────────────────────────────────────────────────────────────
    if token_required and cmd.get("token") != token_required:
        write_result(cmd_id, {"exit_code": -1, "error": "bridge token mismatch"})
        log(f"  ✗ {cmd_id}: token mismatch")
        cmd_path.rename(PROCESSED / cmd_path.name)
        return

    # ─── validate script path ─────────────────────────────────────────────────
    script = cmd.get("script", "")
    if not SAFE_NAME.match(script):
        write_result(cmd_id, {"exit_code": -1, "error": f"script path not allowed: {script!r}"})
        log(f"  ✗ {cmd_id}: bad script path {script!r}")
        cmd_path.rename(PROCESSED / cmd_path.name)
        return

    # SAFE_NAME guarantees "scripts/..." — strip and join under SCRIPTS_DIR.
    script_rel = script[len("scripts/"):]
    script_full = (SCRIPTS_DIR / script_rel).resolve()
    # Defence-in-depth: ensure the resolved path is still under SCRIPTS_DIR
    # (in case symlinks or weird input slipped past the regex).
    try:
        script_full.relative_to(SCRIPTS_DIR.resolve())
    except ValueError:
        write_result(cmd_id, {"exit_code": -1, "error": f"script escapes scripts dir: {script!r}"})
        log(f"  ✗ {cmd_id}: path escape {script!r}")
        cmd_path.rename(PROCESSED / cmd_path.name)
        return

    if not script_full.exists():
        write_result(cmd_id, {"exit_code": -1, "error": f"script does not exist: {script}"})
        log(f"  ✗ {cmd_id}: script not found {script}")
        cmd_path.rename(PROCESSED / cmd_path.name)
        return

    # ─── validate args ────────────────────────────────────────────────────────
    args = cmd.get("args", [])
    if not isinstance(args, list) or not all(isinstance(a, (str, int, float)) for a in args):
        write_result(cmd_id, {"exit_code": -1, "error": "args must be a list of strings/numbers"})
        cmd_path.rename(PROCESSED / cmd_path.name)
        return

    # ─── build cmdline ────────────────────────────────────────────────────────
    if script.endswith(".sh"):
        argv = ["bash", str(script_full), *map(str, args)]
    else:  # .py
        argv = [sys.executable, str(script_full), *map(str, args)]

    timeout = min(int(cmd.get("timeout", 60)), MAX_TIMEOUT_SEC)
    cwd = cmd.get("cwd", str(BRIDGE_ROOT))
    extra_env = cmd.get("env", {}) or {}

    log(f"  → {cmd_id}: {script} {args}")
    env = load_env()
    env.update({str(k): str(v) for k, v in extra_env.items()})

    try:
        proc = subprocess.run(
            argv, capture_output=True, text=True, timeout=timeout,
            cwd=cwd, env=env,
        )
        result = {
            "exit_code": proc.returncode,
            "stdout": proc.stdout[-65536:],
            "stderr": proc.stderr[-65536:],
        }
    except subprocess.TimeoutExpired as e:
        def _decode(x):
            if x is None:
                return ""
            if isinstance(x, bytes):
                return x.decode("utf-8", "replace")
            return x
        result = {
            "exit_code": -2,
            "error": f"timeout after {timeout}s",
            "stdout": _decode(e.stdout)[-65536:],
            "stderr": _decode(e.stderr)[-65536:],
        }
    except Exception as e:
        result = {"exit_code": -3, "error": str(e)}

    write_result(cmd_id, result)
    cmd_path.rename(PROCESSED / cmd_path.name)
    log(f"  ✓ {cmd_id}: exit={result['exit_code']}")


def main() -> int:
    for d in (BRIDGE_ROOT, QUEUE, RESULTS, PROCESSED, SCRIPTS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    env = load_env()
    token = env.get("BRIDGE_TOKEN") or None
    if not token:
        if not ALLOW_UNAUTH:
            log("!! BRIDGE_TOKEN not set and BRIDGE_ALLOW_UNAUTH != 1 — refusing to start.")
            log("   Either set BRIDGE_TOKEN in env or in $BRIDGE_ROOT/.env, or set")
            log("   BRIDGE_ALLOW_UNAUTH=1 for local dev (NEVER for shared machines).")
            return 1
        log("!! BRIDGE_TOKEN not set, BRIDGE_ALLOW_UNAUTH=1 — accepting unauthenticated commands.")
    else:
        log(f"   bridge token loaded (len={len(token)}, prefix={token[:6]}…)")

    log(f"   BRIDGE_ROOT  = {BRIDGE_ROOT}")
    log(f"   SCRIPTS_DIR  = {SCRIPTS_DIR}")
    log(f"daemon up — polling {QUEUE} every {POLL_SEC}s. ctrl+c to stop.")

    stop = False

    def sigint(*_a):
        nonlocal stop
        stop = True
        log("stop requested — finishing current cycle…")

    signal.signal(signal.SIGINT, sigint)
    signal.signal(signal.SIGTERM, sigint)

    while not stop:
        try:
            files = sorted(QUEUE.glob("*.json"))
            for f in files:
                run_one(f, token)
        except Exception as e:
            log(f"! daemon loop error: {e}")
        time.sleep(POLL_SEC)

    log("daemon exiting")
    return 0


if __name__ == "__main__":
    sys.exit(main())
