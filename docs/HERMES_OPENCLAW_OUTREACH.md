# Hermes & Open Claw Outreach — GitHub Issue Templates

## Status

✅ **Bridge implementation complete with MCP server**
⏳ **GitHub issue posting: manual steps below** (API authentication issues with gh CLI)

---

## Issue #1: Post to Hermes Repository

**Repository:** Find the official Hermes repo (likely `hermes-agent/hermes` or `NousResearch/hermes-agent`)

**Title:**
```
Direct integration: MCP provider for Claude Code subscription (no API keys)
```

**Body:**
```markdown
## Problem

As of April 4, 2026, you can't connect Hermes directly to Claude Max/Pro subscription. Current options require either:
- **Separate API billing** (costs, no local context)
- **OAuth workarounds** (fragile, only extra usage credits)
- **Alternative models** (OpenAI, Copilot)

This limits Hermes agents' access to Claude's capabilities.

## Solution: Use cowork-to-code-bridge as MCP Provider

**cowork-to-code-bridge** is an open-source daemon that bridges Claude Cowork and Claude Code on your machine. We've just added an **MCP (Model Context Protocol) server** that Hermes can connect to directly.

**Result:** Hermes agents can now escalate work to Claude Code subscription via a local MCP provider. No API keys. No separate billing. Full context (your repos, shell, MCPs).

## How It Works

**Hermes Config:**

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
# Hand off complex task to Claude Code
response = hermes.escalate(
    tool="escalate_to_claude",
    request="Debug the API failure and fix it",
    wait_seconds=600
)
# Returns: {"status": "completed", "result": {...}}
```

## MCP Tools Provided

1. **escalate_to_claude** — Hand a task to Claude Code, get result asynchronously
2. **run_script** — Execute a whitelisted script directly
3. **list_bridge_scripts** — Discover available scripts

## Why This Matters

| Metric | Hermes + API Key | Hermes + Bridge MCP |
|---|---|---|
| **Billing** | Usage-based (separate) | Included in Max plan |
| **Local context** | No (cloud API) | Yes (full Claude Code access) |
| **Daemon required** | No (stateless) | Yes (runs on your machine) |
| **Setup** | Paste API key | Install bridge + add MCP config |
| **Best for** | Quick queries | Complex debugging, code review |

## Reference Implementation

The bridge is production-ready:
- ✅ MCP JSONRPC 2.0 over stdio
- ✅ Token-authenticated
- ✅ Idempotent, crash-resilient
- ✅ Tested (9 unit tests + manual verification)
- ✅ Works on macOS, Linux, WSL2

**GitHub:** https://github.com/abhinaykrupa/cowork-to-code-bridge
**MCP Docs:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/MCP_SERVER_IMPLEMENTATION.md
**Config Example:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/examples/hermes-mcp-config.json
**External Agent Integration Guide:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/EXTERNAL_AGENT_INTEGRATION.md

## What We're Proposing

1. **Link from Hermes docs** to the bridge as an integration option
2. **Add example** showing Hermes config + escalation pattern
3. **We link back** to Hermes as a reference implementation

## No Ask of Hermes Repo

The bridge is completely standalone. You don't need to maintain or integrate anything into Hermes. We're just proposing that your docs mention this option for users who want Claude Code integration without API keys.

---

**Want to try it?**
```bash
# Install bridge
curl -fsSL https://raw.githubusercontent.com/abhinaykrupa/cowork-to-code-bridge/main/install.sh | bash

# Start MCP server
cowork-to-code-bridge-mcp --stdio
```
```

---

## Issue #2: Post to Open Claw Repository

**Repository:** `OpenClaw/openclaw` (or `open-claw/openclaw`)

**Title:**
```
Direct integration: MCP provider for Claude Code subscription (no tokens)
```

**Body:**
```markdown
## Problem

Open Claw can no longer reuse Claude CLI auth to reach your Claude Max/Pro subscription (as of April 4, 2026). Current paths require:
- **Agent SDK with API key** (billed separately, no local context)
- **Claude CLI workarounds** (fragile, may violate ToS)

This limits Open Claw's access to Claude subscription.

## Solution: Use cowork-to-code-bridge as MCP Provider

**cowork-to-code-bridge** is an open-source daemon that bridges Claude Cowork and Claude Code on your machine. It now provides an **MCP (Model Context Protocol) server** for direct integration.

**Result:** Open Claw workflows can now query Claude Code subscription via MCP. No API keys. No separate billing. Full local context.

## How It Works

**Open Claw Config:**

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

**Open Claw Workflow:**

```python
# Escalate to Claude Code for complex task
result = workflow.escalate(
    tool="escalate_to_claude",
    request="Build and test the project",
    wait_seconds=1800
)
# result = {"status": "completed", "result": {...}}
```

## MCP Tools

1. **escalate_to_claude** — Escalate to Claude Code, get result
2. **run_script** — Execute whitelisted scripts directly
3. **list_bridge_scripts** — Discover available scripts

## Why This Matters

| Aspect | Open Claw + API | Open Claw + Bridge MCP |
|---|---|---|
| **Cost** | Usage-based (separate) | Included in Max plan |
| **Local execution** | No (cloud API) | Yes (full shell, repos, MCPs) |
| **Setup** | Configure API key | Install bridge + add MCP config |
| **Best for** | Cloud-only tasks | Tasks needing local context |

## Reference Implementation

Production-ready:
- ✅ JSONRPC 2.0 over stdio
- ✅ Token-authenticated
- ✅ Idempotent, crash-resilient
- ✅ Full test coverage
- ✅ macOS, Linux, WSL2

**GitHub:** https://github.com/abhinaykrupa/cowork-to-code-bridge
**MCP Docs:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/MCP_SERVER_IMPLEMENTATION.md
**Config Example:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/examples/openclaw-mcp-config.json
**Integration Guide:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/EXTERNAL_AGENT_INTEGRATION.md

## What We're Proposing

1. **Mention in Open Claw docs** as integration path for Claude Code
2. **Link to reference implementation**
3. **We link back** as example use case

## No Ask of Open Claw Repo

Completely standalone. No maintenance or code changes needed in Open Claw. Just a docs link for users wanting to use their Max plan.
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
