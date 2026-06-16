# Manual GitHub Issue Creation Instructions

The cowork-to-code-bridge repo has been updated with Hermes/Open Claw integration support. 
Below are the exact issues to create on external repos.

---

## Issue 1: Post to Hermes Repository

**Repo:** https://github.com/hermes-agent/hermes (or wherever Hermes is hosted)

**Title:**
```
Escalate from Hermes to Claude Code subscription via file-based bridge (no API keys)
```

**Body:**
```markdown
### Problem

You can't connect Hermes directly to Claude Max/Pro subscription anymore (as of April 4, 2026). Current options:
- **API key:** Billed separately from subscription; loses local context (repos, shell, MCPs).
- **OAuth:** Only works on "extra usage" credits, not base allowance.
- **Alternative model:** Use OpenAI/Copilot instead of Claude.

This means Hermes agents either run on separate billing or lose Claude's capabilities.

### Solution

**cowork-to-code-bridge** — a file-based async queue that lets Hermes hand off complex tasks to Claude Code running on your machine, using your subscription with zero extra cost and zero API keys.

#### How it works

1. **Hermes detects an issue** (failed build, anomalous metrics, etc.)
2. **Hermes escalates** via `escalate_to_claude.sh "Debug X"` (writes JSON to local queue folder)
3. **Claude Code picks it up** from inbox when a Cowork chat is open
4. **Agent debugs/fixes** with full file/shell/MCP access
5. **Result written back** to reply folder
6. **Hermes resumes** with the fix applied

#### Example

```python
# In a Hermes agent
result = subprocess.run([
    "escalate_to_claude.sh",
    f"API health check failing. Fix /Users/me/projects/api/health.py and restart.",
    "--wait", "600"
], capture_output=True, text=True)

# Claude Code just debugged and fixed it; Hermes applies the result
```

### Reference Implementation

The bridge is production-ready:
- ✅ Token-authenticated file-based queue
- ✅ Idempotent, crash-resilient (journal + markers)
- ✅ macOS (launchd), Linux (systemd/manual), WSL2
- ✅ PyPI + Homebrew
- ✅ Full test suite

**GitHub:** https://github.com/abhinaykrupa/cowork-to-code-bridge
**Docs:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/HERMES_PITCH.md
**Installation:** One-liner; then agents can call `escalate_to_claude.sh`

### What we're proposing

1. **Link from Hermes docs** to the bridge as a recommended way to reach Claude Code subscription (vs. API key or alternatives).
2. **Add integration example** to Hermes docs if you adopt it (how to detect error → escalate → resume).
3. **We link back** to Hermes as a reference implementation (helps both repos gain visibility).

### No ask of Hermes repo

You don't have to maintain anything or add code to Hermes. The bridge is standalone and independent. We're just proposing that your docs mention it as an option for users who want to use Claude Code subscription with Hermes.
```

---

## Issue 2: Post to Open Claw Repository

**Repo:** https://github.com/OpenClaw/openclaw

**Title:**
```
Reach Claude Code subscription from Open Claw via file-based bridge (no tokens)
```

**Body:**
```markdown
### Problem

Open Claw can no longer reuse Claude CLI auth to tap your Claude Max/Pro subscription (as of April 4, 2026). Current paths:
- **Agent SDK:** Configure as API provider; billed separately from subscription.
- **Claude CLI proxy:** Workarounds are fragile and may violate ToS.

Open Claw agents either lose subscription access or end up on separate billing.

### Solution

**cowork-to-code-bridge** — a file-based async queue that lets Open Claw hand off work to Claude Code running on your machine, using your subscription with zero tokens and zero API keys.

#### How it works

1. **Open Claw detects a task** that needs local execution (run code, debug, review)
2. **Open Claw writes to bridge queue** via `request_cowork.sh` or `escalate_to_claude.sh`
3. **Claude Code picks it up** from inbox when a Cowork chat is open
4. **Agent executes locally** with full file/shell/MCP access
5. **Result written back** to reply folder
6. **Open Claw resumes** with the output

#### Example

```python
# In an Open Claw workflow
if task_needs_local_execution:
    result = subprocess.run([
        "request_cowork.sh",
        f"Build and test the project in {repo_path}",
        "--wait", "900"
    ], capture_output=True, text=True)
    
    # Claude Code just ran the build on your machine
    assert_build_passed(result.stdout)
```

### Reference Implementation

The bridge is production-ready and open-source:
- ✅ Token-authenticated file-based queue
- ✅ Idempotent, crash-resilient (journal + markers)
- ✅ macOS (launchd), Linux (systemd/manual), WSL2
- ✅ PyPI + Homebrew
- ✅ Full test suite

**GitHub:** https://github.com/abhinaykrupa/cowork-to-code-bridge
**PyPI:** https://pypi.org/project/cowork-to-code-bridge/
**Docs:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/RECIPES.md

### What we're proposing

1. **Mention in Open Claw docs** as an alternative to API keys for reaching Claude Code on your machine.
2. **Link to reference implementation** (bridge repo).
3. **We link back** to Open Claw as an example use case (mutual visibility).

### No ask of Open Claw repo

The bridge is completely standalone. You don't need to add code or maintain anything. We're suggesting a docs link for users who want to keep their Claude Max subscription separate from Open Claw billing.
```

---

## Summary

✅ **Bridge repo updated:**
- Added `escalate_to_claude.sh` starter script (examples/allowed_scripts/)
- Expanded RECIPES.md with Hermes + external tool integration patterns
- Updated README hero pitch to highlight agent integration
- Created detailed HERMES_PITCH.md for reference
- Committed and pushed to main

📋 **Next steps (manual):**
1. Post Issue #1 to Hermes repo (find correct GitHub URL)
2. Post Issue #2 to Open Claw repo (https://github.com/OpenClaw/openclaw)
3. Monitor for responses and engagement

**Note:** The bridge is now ready for external agents to use. The pitch is clear, the docs are comprehensive, and the implementation is production-ready (token-authenticated, idempotent, crash-resilient).
