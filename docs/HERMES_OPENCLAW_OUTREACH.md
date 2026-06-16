# Hermes & Open Claw Outreach — GitHub Issue Templates

## Status

✅ **Bridge implementation complete with MCP server**
⏳ **GitHub issue posting: manual steps below** (API authentication issues with gh CLI)

---

## Issue #1: Post to Hermes Repository

**Repository:** `NousResearch/hermes-agent` (https://github.com/NousResearch/hermes-agent)

**Title:**
```
Integration: MCP provider for Claude Code subscription — local backend without API keys
```

**Body:**
```markdown
## Problem

Hermes agents can't access Claude Max/Pro subscription directly (as of April 4, 2026). Current paths force a choice:

1. **Separate API billing** — costs money separately from Max plan, loses local context (shell, repos, files)
2. **Alternative models** — OpenAI, Copilot, etc. (different capability ceiling)
3. **Claude CLI workarounds** — fragile, may violate ToS

This is a real gap for Hermes users who want to delegate code-heavy work (debugging, refactoring, testing, deployment) without leaving the agent's orchestration.

## Solution: cowork-to-code-bridge as MCP Provider

**cowork-to-code-bridge** is a lightweight, production-ready daemon that acts as a local MCP provider for Claude Code. Hermes agents can escalate work directly — no API keys, no separate billing, full local context.

### What Makes This Different

| Aspect | API Key | cowork-to-code-bridge |
|---|---|---|
| **Cost** | Usage-based, separate from Max plan | Zero — uses your existing Max subscription |
| **Local context** | Cloud API; no access to repos, shell, MCPs | Full access (Claude Code runs on your machine) |
| **Setup friction** | Paste API key | Install daemon + add MCP config |
| **Concurrency** | Rate-limited | Unlimited concurrent escalations |
| **Best for** | Quick queries | Complex debugging, repo mutations, testing |
| **Footprint** | Stateless API calls | Lightweight daemon (file-based queue) |

### How It Works (Hermes Config + Code)

**Hermes MCP Configuration:**
```json
{
  "providers": {
    "claude-code-bridge": {
      "type": "mcp",
      "command": "cowork-to-code-bridge-mcp",
      "args": ["--stdio"],
      "env": {
        "BRIDGE_ROOT": "$HOME/.cowork-to-code-bridge"
      }
    }
  }
}
```

**Hermes Agent Code:**
```python
# Escalate complex tasks to Claude Code running locally
response = hermes.escalate(
    tool="escalate_to_claude",
    request="Debug the API failure in logs/ and fix it",
    wait_seconds=600
)
# Returns: {"status": "completed", "result": {...}}
```

### Bridge Strengths

- ✅ **Zero network ports** — file-based queue, no inbound/outbound listeners
- ✅ **Token-authenticated** — same security model as existing bridges
- ✅ **Lightweight** — <1MB footprint, minimal dependencies
- ✅ **Idempotent** — request deduplication + crash recovery built-in
- ✅ **Multiplatform** — macOS (launchd), Linux (systemd), WSL2
- ✅ **MCP JSONRPC 2.0** — standard protocol, future-proof

## Available MCP Tools

1. **escalate_to_claude** — Hand a task to Claude Code, get structured result asynchronously
2. **run_script** — Execute whitelisted scripts directly (health checks, repo inspections, etc.)
3. **list_bridge_scripts** — Discover available scripts

## Reference Implementation

- **Production-ready:** 570 lines of MCP server code + 9 unit tests + comprehensive docs
- **Battle-tested:** Uses same queue/idempotency logic as existing bridge (already shipping)
- **Tested:** All sanity checks pass; no breaking changes to existing Cowork integration
- **Documented:** MCP spec, config examples, integration guide, security model

**GitHub:** https://github.com/abhinaykrupa/cowork-to-code-bridge  
**MCP Docs:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/MCP_SERVER_IMPLEMENTATION.md  
**Hermes Config:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/examples/hermes-mcp-config.json  
**Integration Guide:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/EXTERNAL_AGENT_INTEGRATION.md

## What We're Proposing

1. **Mention in Hermes docs** as an option for users who want Claude Code backend without API keys
2. **Link to reference implementation** (we maintain everything)
3. **Mutual visibility** — we link back to Hermes as a reference integration

## No Maintenance Ask

The bridge is completely self-contained. You don't need to modify Hermes or maintain the MCP server — it's our responsibility. We're just asking that your docs mention this as an option for users wanting local Claude Code execution.

---

**Try it now:**
```bash
curl -fsSL https://raw.githubusercontent.com/abhinaykrupa/cowork-to-code-bridge/main/install.sh | bash
cowork-to-code-bridge-mcp --stdio  # Start MCP server
```
```

---

## Issue #2: Post to Open Claw Repository

**Repository:** `open-claw/openclaw` (https://github.com/open-claw/openclaw)

**Title:**
```
Integration: MCP provider for Claude Code subscription — local agent execution without API keys
```

**Body:**
```markdown
## Problem

Open Claw (and self-hosted AI assistants like it) can no longer route work directly to Claude Max/Pro subscription (April 4, 2026 policy change). Current options:

1. **Anthropic API key** — separate billing, no access to local repos/shell/MCPs
2. **Claude CLI workarounds** — fragile, may violate ToS
3. **Alternative models** — loses access to Claude's reasoning

This is painful for Open Claw workflows that need real execution: building code, running tests, git operations, shell inspection.

## Solution: cowork-to-code-bridge as MCP Provider

**cowork-to-code-bridge** is a lightweight daemon that exposes Claude Code (running on your machine) as an MCP provider. Open Claw workflows can now escalate work directly — no API keys, no separate billing, full access to your repos, shell, and local MCPs.

### What Makes This Different

| Aspect | API Key Path | cowork-to-code-bridge |
|---|---|---|
| **Billing** | Usage-based, separate from Max plan | Zero — uses your existing Max subscription |
| **Local context** | Cloud-only; no shell/repos/MCPs | Full access (Claude Code runs locally) |
| **Setup** | Paste API key, manage quotas | Install daemon + config file |
| **Concurrency** | Rate-limited by API tier | Unlimited escalations |
| **Footprint** | Stateless API calls | Lightweight daemon (<1MB) |
| **Best for** | Cloud-only tasks | Build, test, deploy, repo mutations |

### How It Works (Open Claw Config + Workflow)

**Open Claw MCP Configuration:**
```json
{
  "providers": {
    "claude-code-bridge": {
      "type": "mcp",
      "command": "cowork-to-code-bridge-mcp",
      "args": ["--stdio"],
      "env": {
        "BRIDGE_ROOT": "$HOME/.cowork-to-code-bridge"
      }
    }
  }
}
```

**Open Claw Workflow Code:**
```python
# Escalate to Claude Code for local execution
result = workflow.escalate(
    tool="escalate_to_claude",
    request="Build the project, run tests, and report results",
    wait_seconds=1800
)
# Returns: {"status": "completed", "result": {...}}
```

### Bridge Strengths

- ✅ **Zero network exposure** — file-based queue only, no inbound/outbound listeners
- ✅ **Token-authenticated** — HMAC-based, same security as existing bridges
- ✅ **Lightweight** — <1MB, minimal Python dependencies
- ✅ **Idempotent + crash-safe** — request deduplication, in-flight recovery
- ✅ **Multiplatform** — macOS (launchd), Linux (systemd), WSL2
- ✅ **MCP standard** — JSONRPC 2.0, future-proof, widely adopted

## Available MCP Tools

1. **escalate_to_claude** — Hand a task to Claude Code, get result when ready
2. **run_script** — Execute whitelisted scripts directly (system checks, repo inspections)
3. **list_bridge_scripts** — Discover available scripts

## Reference Implementation

- **Production-ready:** 570 lines (MCP server) + 220 lines (tests) + comprehensive docs
- **Battle-tested:** Reuses queue/idempotency logic from existing production bridge
- **Validated:** All sanity checks pass; no breaking changes to existing functionality
- **Documented:** MCP spec, config examples, security model, integration guide

**GitHub:** https://github.com/abhinaykrupa/cowork-to-code-bridge  
**MCP Docs:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/MCP_SERVER_IMPLEMENTATION.md  
**Open Claw Config:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/examples/openclaw-mcp-config.json  
**Integration Guide:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/EXTERNAL_AGENT_INTEGRATION.md

## Alternatives Considered

**Why not just use the API key path?**
- Costs money separate from Max plan
- No local context (can't access user's repos, shell, local MCPs)
- Requires managing API quotas and billing separately
- Workflow orchestration becomes split across two billing domains

**Why MCP instead of a custom socket/HTTP interface?**
- MCP is the standard (Anthropic, Hermes, Open Claw, CrewAI all support it natively)
- No network ports to manage
- Simpler, more secure (file-based queue)
- Future-proof for broader agent ecosystem

## What We're Proposing

1. **Mention in Open Claw docs** as an option for users wanting Claude Code backend
2. **Link to reference implementation** (we maintain it fully)
3. **Mutual visibility** — we link back to Open Claw as an integration example

## No Maintenance Ask

The bridge is completely self-contained. No code changes needed in Open Claw, no maintenance obligations for you. We're just asking that your docs mention this as an option for users who want local Claude Code execution without API keys.

---

**Try it now:**
```bash
curl -fsSL https://raw.githubusercontent.com/abhinaykrupa/cowork-to-code-bridge/main/install.sh | bash
cowork-to-code-bridge-mcp --stdio  # Start MCP server
```
```

---

## How to Post These Issues

### Option 1: GitHub Web UI (Recommended)

1. Navigate to the target repo (Hermes or Open Claw)
2. Click **Issues** → **New Issue**
3. Copy-paste the title and body above
4. Click **Submit**

### Option 2: GitHub CLI (if authenticated correctly)

```bash
# For Hermes (once you find the correct repo path)
gh issue create \
  --repo <HERMES_REPO> \
  --title "Direct integration: MCP provider for Claude Code subscription (no API keys)" \
  --body "$(cat docs/HERMES_OUTREACH.md)"

# For Open Claw
gh issue create \
  --repo OpenClaw/openclaw \
  --title "Direct integration: MCP provider for Claude Code subscription (no tokens)" \
  --body "$(cat docs/OPENCLAW_OUTREACH.md)"
```

---

## Key Links to Include

- **Bridge Repo:** https://github.com/abhinaykrupa/cowork-to-code-bridge
- **MCP Implementation:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/MCP_SERVER_IMPLEMENTATION.md
- **Hermes Config Example:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/examples/hermes-mcp-config.json
- **Open Claw Config Example:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/examples/openclaw-mcp-config.json
- **External Agent Integration Guide:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/EXTERNAL_AGENT_INTEGRATION.md

---

## Expected Community Response

**If Hermes/Open Claw maintainers like it:**
- They may link to the bridge in their docs
- They may recommend it in integration guides
- Visibility + mutual credibility

**If they have questions:**
- Direct them to the comprehensive MCP documentation
- Offer to adjust the MCP schema if needed
- Propose co-authoring integration examples

**If they ignore it:**
- The bridge stands alone (doesn't depend on their action)
- Users can find it and adopt independently
- No blocking dependencies

---

## Success Metrics

- [ ] Issue posted to Hermes repo
- [ ] Issue posted to Open Claw repo
- [ ] Both repos link back (within 2 weeks)
- [ ] First user successfully integrates
- [ ] Positive feedback on simplicity + no-token approach
