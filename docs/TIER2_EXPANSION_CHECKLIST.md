# Tier 2 Expansion — Additional High-Visibility Frameworks

Status: Ready to post (all issues drafted)

---

## Tier 2A: Microsoft & OpenAI Official Frameworks (VERY HIGH IMPACT)

### 1. Microsoft Agent Framework (microsoft/agent-framework)

**Repository:** https://github.com/microsoft/agent-framework  
**Issue Template:** Feature Request  
**Priority:** ⭐⭐⭐⭐⭐ (official Microsoft framework)

**Title:**
```
Integration: MCP provider for Claude Code — local execution backend for Microsoft Agent Framework
```

**Body:**
```markdown
## Problem

Microsoft Agent Framework users orchestrating complex multi-step tasks want to leverage Claude Code capabilities, but current options require:
- **Separate Claude API billing** — costs money outside existing subscription
- **Loss of local context** — no access to user's repos, shell, MCPs, local environment
- **Complex credential management** — separate API keys and quota tracking

## Solution: cowork-to-code-bridge as MCP Provider

**cowork-to-code-bridge** is a lightweight, production-ready daemon that exposes Claude Code (running on the user's machine) as an MCP provider. Microsoft Agent Framework workflows can now escalate work directly—no API keys, no separate billing, full local context.

### How It Works

**MCP Configuration:**
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

**Agent Framework Code:**
```python
# Escalate to local Claude Code
response = agent.escalate(
    tool="escalate_to_claude",
    request="Complete the task with full repo context",
    wait_seconds=1800
)
```

### Why This Matters for Microsoft Agent Framework

Agent Framework users need a reliable, cost-effective local execution backend. This bridge solves exactly that: use Claude Code subscription users already have, access full local context (repos, shell, MCPs), no extra billing or credential management. Perfect for enterprise workflows where local execution is a requirement.

### Bridge Strengths

- ✅ **Zero network ports** — file-based queue, no inbound/outbound listeners
- ✅ **Token-authenticated** — HMAC-based security
- ✅ **Lightweight** — <1MB, minimal dependencies
- ✅ **Idempotent + crash-safe** — request deduplication, in-flight recovery
- ✅ **Multiplatform** — macOS, Linux, WSL2
- ✅ **MCP standard** — JSONRPC 2.0, compatible with Agent Framework

### Available MCP Tools

1. **escalate_to_claude** — Hand a task to Claude Code, get result asynchronously
2. **run_script** — Execute whitelisted scripts directly
3. **list_bridge_scripts** — Discover available scripts

## Reference Implementation

- **Production-ready:** 570 lines MCP server + 9 unit tests + comprehensive docs
- **Battle-tested:** Uses proven queue/idempotency patterns
- **Validated:** All sanity checks pass
- **Documented:** MCP spec, config examples, security model

**GitHub:** https://github.com/abhinaykrupa/cowork-to-code-bridge  
**MCP Docs:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/MCP_SERVER_IMPLEMENTATION.md  
**Integration Guide:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/EXTERNAL_AGENT_INTEGRATION.md

## What We're Proposing

1. **Mention in Agent Framework docs** as local execution backend option
2. **Link to reference implementation** (we maintain it)
3. **Mutual visibility** — we link back to Agent Framework

## No Maintenance Ask

Bridge is completely self-contained. No code changes needed, no maintenance obligations. Just asking for docs mention + link.

---

**Try it now:**
```bash
curl -fsSL https://raw.githubusercontent.com/abhinaykrupa/cowork-to-code-bridge/main/install.sh | bash
cowork-to-code-bridge-mcp --stdio
```
```

---

### 2. OpenAI Agents (openai/openai-agents-python)

**Repository:** https://github.com/openai/openai-agents-python  
**Issue Template:** Feature Request  
**Priority:** ⭐⭐⭐⭐⭐ (official OpenAI SDK)

**Title:**
```
Integration: MCP provider for Claude Code — extend OpenAI Agents with local Claude backend
```

**Body:** (Use template above, customize for OpenAI context)

**Custom Key Message:**
```
### Why This Matters for OpenAI Agents

OpenAI Agents users often want to access multiple LLM providers for different tasks. This bridge enables seamless integration of Claude Code capabilities (powerful reasoning + code generation) as a local execution backend—no API key management, no separate billing, full access to user's local environment. Complements OpenAI's models by providing a credible alternative for code-heavy workloads.
```

---

## Tier 2B: Fast-Growing, Well-Funded Frameworks (HIGH IMPACT)

### 3. AutoGPT (Significant-Gravitas/AutoGPT)

**Repository:** https://github.com/Significant-Gravitas/AutoGPT  
**Issue Template:** Feature Request  
**Priority:** ⭐⭐⭐⭐ (highly visible autonomous agent)

**Title:**
```
Integration: MCP provider for Claude Code in AutoGPT — local code execution, no API keys
```

**Body:** (Use master template, customize for AutoGPT)

**Custom Key Message:**
```
### Why This Matters for AutoGPT

AutoGPT users running autonomous agents need reliable, cost-effective local code execution. This bridge provides exactly that: Claude Code subscription becomes the execution backend (no separate API billing, full local context). Especially valuable for AutoGPT's autonomous loops where delegation to a powerful reasoning model is the natural next step.
```

---

### 4. MetaGPT (FoundationAgents/MetaGPT)

**Repository:** https://github.com/FoundationAgents/MetaGPT  
**Issue Template:** Feature Request  
**Priority:** ⭐⭐⭐⭐ (software company in a box)

**Title:**
```
Integration: MCP provider for Claude Code in MetaGPT — local code generation, no API keys
```

**Body:** (Use master template)

**Custom Key Message:**
```
### Why This Matters for MetaGPT

MetaGPT's multi-role software company pattern needs powerful code generation and debugging. This bridge lets MetaGPT workflows escalate code-heavy tasks (architecture design, implementation, testing, debugging) to Claude Code running locally—no API keys, full repo context, same subscription. Perfect for MetaGPT's agent team orchestration.
```

---

### 5. PydanticAI (pydantic/pydantic-ai)

**Repository:** https://github.com/pydantic/pydantic-ai  
**Issue Template:** Feature Request  
**Priority:** ⭐⭐⭐⭐ (pydantic-backed, growing rapidly)

**Title:**
```
Integration: MCP provider for Claude Code in PydanticAI — structured local execution, no API keys
```

**Body:** (Use master template)

**Custom Key Message:**
```
### Why This Matters for PydanticAI

PydanticAI builds structured, tool-using agents on pydantic's validation. This bridge provides a natural local execution backend for code-heavy tasks: Claude Code runs on the user's machine, validates output via pydantic, no API keys needed. Especially powerful for PydanticAI's agent pipeline patterns.
```

---

### 6. Mastra (mastra-ai/mastra)

**Repository:** https://github.com/mastra-ai/mastra  
**Issue Template:** Feature Request  
**Priority:** ⭐⭐⭐⭐ (fast-growing, well-funded)

**Title:**
```
Integration: MCP provider for Claude Code in Mastra — local code execution for agent workflows
```

**Body:** (Use master template)

**Custom Key Message:**
```
### Why This Matters for Mastra

Mastra users building agent workflows need reliable code execution without separate API billing. This bridge solves exactly that: Claude Code runs locally (no API keys), full repo context, leverages user's existing subscription. Perfect for Mastra's workflow orchestration and integration patterns.
```

---

## Tier 2C: MCP-Native & Specialized Frameworks (HIGH IMPACT)

### 7. lastmile-ai/mcp-agent

**Repository:** https://github.com/lastmile-ai/mcp-agent  
**Issue Template:** Feature Request  
**Priority:** ⭐⭐⭐⭐ (MCP-first, direct fit)

**Title:**
```
Integration: cowork-to-code-bridge as MCP server — Claude Code local execution backend
```

**Body:**
```markdown
## Problem

MCP-agent users want to build agents on top of MCP servers, but lack a reliable local execution backend that:
- Doesn't require separate API billing
- Provides full local context (repos, shell, MCPs, files)
- Works seamlessly with MCP protocol

## Solution: cowork-to-code-bridge MCP Server

**cowork-to-code-bridge** is an MCP server that exposes Claude Code (running locally) as an execution backend. Agents built on MCP can now escalate code-heavy work directly.

### How It Works

**Agent Configuration:**
```json
{
  "providers": {
    "claude-code-bridge": {
      "type": "mcp",
      "command": "cowork-to-code-bridge-mcp",
      "args": ["--stdio"]
    }
  }
}
```

**Agent Code:**
```python
response = agent.escalate(
    tool="escalate_to_claude",
    request="Complete the task with full context",
    wait_seconds=1800
)
```

### Why This Matters

mcp-agent users building agents on MCP servers need a native MCP server for local Claude Code execution. This bridge is exactly that: production-ready MCP server, zero network ports, token-authenticated, crash-safe.

### Available MCP Tools

1. **escalate_to_claude** — Hand a task to Claude Code, get result
2. **run_script** — Execute whitelisted scripts directly
3. **list_bridge_scripts** — Discover available scripts

## Reference Implementation

- **Production-ready:** 570 lines MCP server + 9 unit tests
- **Battle-tested:** Uses proven patterns from production bridges
- **Fully documented:** MCP spec, config examples, integration guide

**GitHub:** https://github.com/abhinaykrupa/cowork-to-code-bridge  
**MCP Docs:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/MCP_SERVER_IMPLEMENTATION.md

## What We're Proposing

1. **Feature mcp-agent + bridge** in examples/docs as reference integration
2. **Link to bridge repo** as MCP server reference implementation
3. **Mutual visibility** — we link back as reference MCP integration

---

**Try it now:**
```bash
curl -fsSL https://raw.githubusercontent.com/abhinaykrupa/cowork-to-code-bridge/main/install.sh | bash
cowork-to-code-bridge-mcp --stdio
```
```
```

---

### 8. modelcontextprotocol/servers (Official MCP Repo)

**Repository:** https://github.com/modelcontextprotocol/servers  
**Issue Template:** Feature Request  
**Priority:** ⭐⭐⭐⭐⭐ (official MCP servers repo - HIGH VISIBILITY)

**Title:**
```
Integration: cowork-to-code-bridge — MCP server for local Claude Code execution
```

**Body:**
```markdown
## Overview

**cowork-to-code-bridge** is a production-ready MCP server that exposes Claude Code (running on the user's machine) as an execution backend for agents.

## Why This Matters

Agents using MCP often need local code execution, but lack a reliable option that:
- Uses the user's existing Claude subscription (no separate API billing)
- Provides full local context (repos, shell, MCPs, environment)
- Implements the MCP protocol correctly
- Is production-ready with comprehensive testing

cowork-to-code-bridge solves exactly this: agents can escalate code-heavy work to Claude Code running locally, with full context access and no extra costs.

## Available Tools

1. **escalate_to_claude** — Hand a task to Claude Code, get result asynchronously
2. **run_script** — Execute whitelisted scripts directly
3. **list_bridge_scripts** — Discover available scripts

## Implementation Details

- **JSONRPC 2.0 over stdio** — standard MCP protocol
- **Token-authenticated** — HMAC-based, secure
- **Lightweight** — <1MB, minimal dependencies
- **Idempotent** — request deduplication, crash recovery
- **Multiplatform** — macOS, Linux, WSL2

## Reference

- **GitHub:** https://github.com/abhinaykrupa/cowork-to-code-bridge
- **MCP Implementation:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/MCP_SERVER_IMPLEMENTATION.md
- **Tests:** 9 unit tests covering protocol, tools, edge cases

## Suggested Integration

Consider listing cowork-to-code-bridge in the official MCP servers registry as a reference implementation for "local code execution backend."

---

**Try it now:**
```bash
curl -fsSL https://raw.githubusercontent.com/abhinaykrupa/cowork-to-code-bridge/main/install.sh | bash
cowork-to-code-bridge-mcp --stdio
```
```

---

## Tier 2D: Emerging Frameworks (GOOD FIT)

### 9. VoltAgent (voltagent/voltagent)

**Repository:** https://github.com/voltagent/voltagent  
**Issue Template:** Feature Request  
**Priority:** ⭐⭐⭐ (TypeScript agent framework)

**Title:**
```
Integration: MCP provider for Claude Code — local execution backend for VoltAgent
```

**Body:** (Use master template, customize for TypeScript context)

---

### 10. Upsonic (Upsonic/Upsonic)

**Repository:** https://github.com/Upsonic/Upsonic  
**Issue Template:** Feature Request  
**Priority:** ⭐⭐⭐ (explicitly supports MCP)

**Title:**
```
Integration: cowork-to-code-bridge MCP — Claude Code local execution for Upsonic workflows
```

**Body:** (Use master template, emphasize native MCP support)

---

## Posting Strategy

### Recommended Phases

**Phase A (Immediate):** Microsoft + OpenAI official frameworks
- Microsoft Agent Framework
- OpenAI Agents (Python)
- modelcontextprotocol/servers (official MCP repo)

**Phase B (Following Week):** Fast-growing frameworks
- AutoGPT
- MetaGPT
- PydanticAI
- Mastra

**Phase C (Week 2):** MCP-native + emerging
- lastmile-ai/mcp-agent
- VoltAgent
- Upsonic

### Expected Timeline

- **Phase A:** 3 repos, ~15 min
- **Phase B:** 4 repos, ~20 min
- **Phase C:** 3 repos, ~15 min
- **Total:** 10 new repos, ~50 min

### Success Metrics

- ✅ Issues posted to all Phase A repos
- ✅ Official MCP repo acknowledges integration
- ✅ 50%+ response rate from official frameworks
- ✅ At least 1 repo mentions bridge in docs
- ✅ Cross-linking established (mutual visibility)

---

## Tracking

| Repo | Tier | Status | Issue # | Date | Notes |
|---|---|---|---|---|---|
| Microsoft Agent Framework | 2A | ⏳ Ready | — | — | Official Microsoft framework |
| OpenAI Agents | 2A | ⏳ Ready | — | — | Official OpenAI SDK |
| modelcontextprotocol/servers | 2A | ⏳ Ready | — | — | Official MCP registry (HIGH VALUE) |
| AutoGPT | 2B | ⏳ Ready | — | — | Highly visible autonomous agent |
| MetaGPT | 2B | ⏳ Ready | — | — | Software company in a box |
| PydanticAI | 2B | ⏳ Ready | — | — | Pydantic-backed, growing fast |
| Mastra | 2B | ⏳ Ready | — | — | Fast-growing, well-funded |
| lastmile-ai/mcp-agent | 2C | ⏳ Ready | — | — | MCP-native, direct fit |
| VoltAgent | 2D | ⏳ Ready | — | — | TypeScript framework |
| Upsonic | 2D | ⏳ Ready | — | — | Native MCP support |

---

## Quick Reference

- **Bridge Repo:** https://github.com/abhinaykrupa/cowork-to-code-bridge
- **MCP Docs:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/MCP_SERVER_IMPLEMENTATION.md
- **Integration Guide:** https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/EXTERNAL_AGENT_INTEGRATION.md
- **Master Templates:** docs/MULTI_FRAMEWORK_OUTREACH.md

