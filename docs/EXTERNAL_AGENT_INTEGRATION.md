# External Agent Integration Guide

## Overview

The cowork-to-code-bridge now supports **bidirectional escalation** from external agents (Hermes, Open Claw, cron jobs, CI/CD pipelines) to Claude Code running on your machine.

**Problem:** External agents can't use your Claude Max/Pro subscription directly anymore (as of April 4, 2026). They either pay separate API fees or use alternative models.

**Solution:** The bridge lets agents hand off complex work to Claude Code via a file-based async queue. No API keys. No separate billing. Full local context.

---

## What's New

### 1. `escalate_to_claude.sh` — Hermes Integration Script

Located in `examples/allowed_scripts/escalate_to_claude.sh`. This wrapper helps external agents (especially Hermes) send requests to Claude Code.

**Usage (from any agent):**

```bash
escalate_to_claude.sh "Debug the API failure and fix it" --wait 600
```

**What it does:**
- Writes structured JSON to `~/.cowork-to-code-bridge/to_cowork/`
- Optionally polls for a reply (up to `--wait` seconds)
- No token needed — uses bridge auth automatically

**Installed by:** `install.sh` (wired into daemon setup)

---

### 2. Enhanced Documentation

#### a. **RECIPES.md** — New Sections

**"Escalate from Hermes / Open Claw to Claude Code"**
- Real example: Hermes detects issue → calls `escalate_to_claude.sh` → Claude Code debugs → Hermes applies fix
- Python integration snippet showing how to parse the reply

**"Connect any external tool (CI/CD, cron, webhook) to Claude Code"**
- Patterns for GitHub Actions, scheduled health checks, webhook handlers
- Links to `request_cowork.sh` for full documentation

#### b. **docs/HERMES_PITCH.md** — Detailed Use Case

- Problem statement: can't use Max subscription with Hermes anymore
- Solution explained with flow diagram (5 steps)
- Billing comparison table (API key vs. bridge)
- Integration example (Python + subprocess)
- Roadmap (sync mode, MCP proxy, rate limiting)
- Installation instructions

#### c. **README.md** — Hero Update

Updated headline: **"Let Claude run code on your real machine — safely — from any Claude chat. Integrate with Hermes, cron jobs, CI/CD, or any daemon."**

---

### 3. GitHub Outreach Templates

#### **docs/GITHUB_ISSUES_MANUAL.md**
Step-by-step guide to manually post issues on:
1. **Hermes repo** — propose bridge as alternative to API keys
2. **Open Claw repo** — propose bridge as token-free Claude Code access

No asks of those repos. Just visibility + mutual linking.

---

## How It Works (4-Leg Loop)

```
Agent (Hermes)          Bridge               Claude Code (Cowork)
     │                    │                          │
     │─ escalate JSON ─────▶ to_cowork/             │
     │                    │                          │
     │                    │◀─ agent checks inbox ───│
     │                    │                          │
     │                    │  reads request          │
     │                    │  debugs / fixes ────────▶ agent works
     │                    │                          │
     │  polls ────────────▶ cowork_results/         │
     │◀─ reply JSON ──────●                          │
     │                                              │
```

**Steps:**
1. **Escalate:** Agent writes JSON request to `to_cowork/` (1 file write)
2. **Pickup:** Claude Code agent checks inbox in Cowork (Step 4 of skill)
3. **Debate:** Agent reads request, does the work locally (full capabilities)
4. **Reply:** Agent writes JSON result to `cowork_results/` (1 file write)
5. **Resume:** Escalating agent polls and gets the result

**Zero network ports. Zero external APIs. Zero new secrets.**

---

## Use Cases

### Hermes + Debug Escalation

```python
# In Hermes agent loop:
if error_severity > threshold:
    result = subprocess.run([
        "escalate_to_claude.sh",
        f"Anomaly detected: {error}. Check logs in {log_path}, find root cause, propose fix.",
        "--wait", "1200"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        fix = json.loads(result.stdout)
        apply_fix(fix["code_changes"])
        restart_service()
```

### CI/CD Escalation

```yaml
# GitHub Actions workflow
- name: Run tests
  run: pytest tests/ || escalate_to_claude.sh "Tests failed. Debug and suggest fixes." --wait 900
```

### Cron Health Check

```bash
#!/bin/bash
# Runs nightly; escalates if system unhealthy

health=$(check_system_metrics)
if [[ $health == "FAIL" ]]; then
  escalate_to_claude.sh "System health check failed: $health. Investigate and suggest fixes."
fi
```

### Multi-Step Workflow (Release Pipeline)

```python
# Hermes orchestrates release
steps = [
    "Update version in pyproject.toml and CHANGELOG",
    "Run full test suite and fix any failures",
    "Tag a release and create GitHub release notes",
]

for step in steps:
    result = escalate_to_claude.sh(step, wait=1800)
    if error(result):
        alert_owner()
```

---

## Production Readiness

The bridge is already shipping:
- ✅ Token-authenticated (HMAC-based, constant-time comparison)
- ✅ Idempotent (request ID + reply tracking)
- ✅ Crash-resilient (append-only journal, in-flight markers)
- ✅ Multiplatform (macOS launchd, Linux systemd, WSL2)
- ✅ PyPI + Homebrew
- ✅ Full test suite (e2e, idempotency, bidirectional, idempotency resume)

### Security

- No network ports opened
- No new secrets (reuses existing bridge token)
- Requests are file-based (local machine only)
- Token in `.env` (600 permission, same as before)
- Escalation context captured (hostname, user, cwd) for audit trail

---

## Implementation Checklist (All Done ✅)

| Item | Status | Details |
|---|---|---|
| `escalate_to_claude.sh` script | ✅ Done | examples/allowed_scripts/, installed by install.sh |
| RECIPES.md sections | ✅ Done | Hermes example + external tool patterns |
| README update | ✅ Done | Hero pitch includes "Hermes, cron, CI/CD" |
| HERMES_PITCH.md | ✅ Done | Detailed use case + billing comparison |
| docs/GITHUB_ISSUES_MANUAL.md | ✅ Done | Templates for Hermes + Open Claw |
| install.sh wiring | ✅ Done | escalate_to_claude.sh in scripts/ |
| Commit pushed to main | ✅ Done | `f978119` + `e457b81` |

---

## Next Steps

### 1. **Manual GitHub Issue Posting** (User Action)

See `docs/GITHUB_ISSUES_MANUAL.md` for exact issue titles + bodies.

- **Hermes repo**: Propose bridge as alternative to API keys for Max subscription
- **Open Claw repo**: Propose bridge as token-free Claude Code access

No code changes needed in those repos; just documentation links.

### 2. **Test with Your Daemon** (Integration Testing)

- Spin up your escalation daemon (which started this whole project)
- Have it call `escalate_to_claude.sh` with a test request
- Verify Claude Code agent picks it up and replies
- Verify daemon resumes with the result

This validates the 4-leg loop end-to-end.

### 3. **Monitor Feedback** (Optional)

If Hermes/Open Claw maintainers respond, you have:
- Clear architecture docs (flow diagrams, examples)
- Working code (no new dependencies)
- Production tests (idempotency, crash resilience, bidirectional)

---

## Reference Links

- **Main repo**: https://github.com/abhinaykrupa/cowork-to-code-bridge
- **RECIPES.md**: docs/RECIPES.md (in repo)
- **HERMES_PITCH.md**: docs/HERMES_PITCH.md (in repo)
- **Issue templates**: docs/GITHUB_ISSUES_MANUAL.md (in repo)
- **Starter script**: examples/allowed_scripts/escalate_to_claude.sh (in repo)
- **PyPI**: https://pypi.org/project/cowork-to-code-bridge/

---

## FAQ

**Q: Does this require changes to Hermes?**
A: No. Hermes just calls `escalate_to_claude.sh` (a shell script). The bridge handles the rest.

**Q: What if Claude Code (Cowork) isn't open?**
A: The request stays queued. When Cowork is opened and the agent checks its inbox, it picks it up. Async, not sync.

**Q: How does billing work?**
A: Uses your Claude Code subscription (your Max plan). No separate API key. No usage-based billing.

**Q: Can I use this outside my local machine?**
A: No. The bridge is file-based (requires access to `~/.cowork-to-code-bridge/`). Must be same machine or NFS mount.

**Q: Is there a size limit on requests/replies?**
A: Not enforced, but the daemon guards command files > 1 MB (OOM protection). Keep requests reasonable (< 10 KB JSON).

**Q: What if the agent crashes mid-escalation?**
A: The bridge has in-flight markers and a journal. On restart, the daemon skips already-processed tasks. The escalating agent's `--wait` timeout will expire, and it can retry with the same request (idempotency key ensures no duplicate execution).
