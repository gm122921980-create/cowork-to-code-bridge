# Starter Template Strategy — Canonical Reference Implementation

Status: Ready to plan + implement
Priority: ⭐⭐⭐⭐⭐ (own the canonical starter, frameworks point to it instead of reinventing)

---

## Strategy Overview

Instead of asking frameworks to integrate the bridge themselves, **create a canonical "starter repo"** that shows the exact integration pattern. Frameworks link to it from their docs. You maintain one copy; they don't need to maintain anything.

**Leverage:** Every framework docs page mentioning "Claude Code integration" or "local execution" can link to your starter.

**Benefit:** You control the narrative + can update integration patterns once instead of coordinating with 20 repos.

---

## Option A: hermes-mcp-bridge-starter (Recommended First)

Minimal example: **Hermes agent + cowork-to-code-bridge MCP + Claude Code**

### What's in the Repo

```
hermes-mcp-bridge-starter/
├── README.md (setup + usage)
├── config/
│   └── hermes-mcp-config.json (ready-to-use MCP config)
├── examples/
│   ├── simple_escalation.py (10-line agent that escalates a task)
│   ├── multi_step_workflow.py (orchestrate multiple escalations)
│   └── debug_api_failure.py (realistic use case)
├── scripts/
│   ├── setup.sh (install bridge + configure)
│   └── run_hermes_agent.sh (start hermes with bridge)
└── tests/
    └── test_escalation.py (verify escalation works)
```

### README.md Template

```markdown
# Hermes + cowork-to-code-bridge Starter

Use Hermes agents with Claude Code subscription via local MCP bridge.

## What This Does

- Hermes agent orchestrates work
- When it needs Claude Code (debugging, coding, testing), it escalates via MCP
- Claude Code runs locally (no API keys)
- Hermes gets the result

## 5-Minute Setup

```bash
# 1. Install bridge
curl -fsSL https://raw.githubusercontent.com/abhinaykrupa/cowork-to-code-bridge/main/install.sh | bash

# 2. Start bridge
cowork-to-code-bridge-mcp --stdio &

# 3. Copy config to Hermes
cp config/hermes-mcp-config.json ~/.hermes/config.json

# 4. Run example agent
python examples/simple_escalation.py
```

## Examples

### Simple Escalation
```python
from hermes import Agent

agent = Agent()
result = agent.escalate(
    tool="escalate_to_claude",
    request="Debug the API failure in logs/",
    wait_seconds=600
)
print(result)
```

### Multi-Step Workflow
```python
agent = Agent()

# Step 1: Write tests
tests = agent.escalate(
    tool="escalate_to_claude",
    request="Write unit tests for the API",
    wait_seconds=300
)

# Step 2: Implement feature
impl = agent.escalate(
    tool="escalate_to_claude",
    request=f"Implement the API based on these tests:\n{tests}",
    wait_seconds=600
)

# Step 3: Deploy
agent.escalate(
    tool="run_script",
    script="deploy.sh"
)
```

## What You Need

- Hermes agent installed
- Claude Code subscription (or sign up)
- Python 3.9+
- macOS, Linux, or WSL2

## How to Integrate

This starter uses **standard MCP protocol** (JSONRPC 2.0) via:
- `cowork-to-code-bridge-mcp` command
- Standard `~/.cowork-to-code-bridge/` bridge directory
- No extra setup required

## Reference

- [Bridge Repo](https://github.com/abhinaykrupa/cowork-to-code-bridge)
- [MCP Docs](https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/MCP_SERVER_IMPLEMENTATION.md)
- [Integration Guide](https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/EXTERNAL_AGENT_INTEGRATION.md)

## License

MIT (same as Hermes)
```

### examples/simple_escalation.py

```python
"""Simplest possible example: escalate a task to Claude Code"""

from hermes import Agent
import json

def main():
    agent = Agent()
    
    # Escalate debugging task to Claude Code
    result = agent.escalate(
        tool="escalate_to_claude",
        request="Debug the API health check endpoint and suggest fixes",
        wait_seconds=600
    )
    
    # Parse result
    if result.get("status") == "completed":
        print("Claude Code completed the task:")
        print(result.get("result"))
    else:
        print(f"Task failed: {result.get('message')}")

if __name__ == "__main__":
    main()
```

### config/hermes-mcp-config.json

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

---

## Option B: mcp-agent-starter (For modelcontextprotocol/servers)

Minimal MCP agent + bridge integration demo.

### What's in the Repo

```
mcp-agent-starter/
├── README.md (MCP quick start)
├── src/
│   ├── agent.py (simple agent using MCP)
│   └── bridge_client.py (MCP client for bridge)
├── config/
│   └── mcp-servers.json (bridge + other MCP servers config)
├── examples/
│   ├── basic_agent.py (connect to MCP, make call)
│   └── multi_server_orchestration.py (use bridge + other servers)
└── tests/
    └── test_mcp_integration.py
```

### Why This is Valuable

- **Reference implementation** for how to use MCP servers in agents
- **Shows bridge in context** (not in isolation)
- **Demonstrates multi-server orchestration** (bridge + FS server + web server, etc.)
- **Official MCP repo can link to it** as a "getting started" guide

### PR to modelcontextprotocol/servers

**Title:**
```
Add mcp-agent-starter to docs/examples — agent framework integration guide
```

**Body:**
```markdown
## Summary

Adding a starter template showing how to build agents on top of MCP servers.
Uses cowork-to-code-bridge as primary example (local Claude Code backend).

## What's included

- Simple agent that discovers + uses MCP servers
- Config showing multiple servers (bridge + FS + web)
- Step-by-step setup guide
- Python example (easy to translate to other languages)

## Value

This shows developers:
1. How to consume MCP servers in their agents
2. Real-world orchestration patterns
3. Why bridge servers (like cowork-to-code-bridge) matter

## Links

- Repo: [mcp-agent-starter](https://github.com/abhinaykrupa/mcp-agent-starter)
- See cowork-to-code-bridge in action: [GitHub](https://github.com/abhinaykrupa/cowork-to-code-bridge)
```

---

## How to Use These Starters in Outreach

### When posting issue to Hermes
```
"For a working example, see: https://github.com/abhinaykrupa/hermes-mcp-bridge-starter"
```

### When posting issue to modelcontextprotocol/servers
```
"Reference implementation: https://github.com/abhinaykrupa/mcp-agent-starter 
(shows building agents on MCP servers, with bridge as primary backend)"
```

### When posting issue to framework docs
```
"Getting started: https://github.com/abhinaykrupa/[framework]-bridge-starter
(ready-to-run example with full setup guide)"
```

### In README.md of main bridge repo
```
## Quick Start by Framework

- **Hermes:** [hermes-mcp-bridge-starter](https://github.com/abhinaykrupa/hermes-mcp-bridge-starter)
- **LangChain:** [langchain-mcp-bridge-starter](https://github.com/abhinaykrupa/langchain-mcp-bridge-starter)
- **MCP Agents:** [mcp-agent-starter](https://github.com/abhinaykrupa/mcp-agent-starter)
```

---

## Implementation Plan

### Phase 1: Create hermes-mcp-bridge-starter (This Week)

1. Create new repo `hermes-mcp-bridge-starter`
2. Add README.md (copy from template above)
3. Add config/ + examples/ (copy from above)
4. Add setup.sh + run_hermes_agent.sh
5. Test locally (Hermes agent actually escalates to bridge)
6. Push to GitHub

**Time:** 2-3 hours
**ROI:** High (Hermes is primary use case, shows it works end-to-end)

### Phase 2: Create mcp-agent-starter (Week 2)

1. Create new repo `mcp-agent-starter`
2. Add README.md + src/ + examples/
3. Show agent discovering + using MCP servers
4. Show bridge in orchestration pattern
5. Test locally
6. **Optional:** PR this to modelcontextprotocol/servers/docs/examples

**Time:** 2-3 hours
**ROI:** Very high (official MCP repo could link to it)

### Phase 3: Framework-Specific Starters (Week 3+)

For each Tier 1 framework (LangChain, LangGraph, AutoGen, etc.):
- Create `[framework]-mcp-bridge-starter` repo
- Show idiomatic usage for that framework
- Quick setup guide
- Ready-to-run examples

**Time per framework:** 1-2 hours
**Total:** 7-14 hours for all 7 frameworks
**ROI:** Medium (frameworks appreciate concrete examples, may link from their docs)

---

## Expected Benefits

✅ **Reference implementations** — Frameworks don't have to figure out integration themselves

✅ **Credibility** — "Works out of the box" with concrete examples

✅ **Discoverability** — Developers searching "[Framework] + Claude Code" find your starters

✅ **Maintenance** — You update patterns once in your starters, all frameworks benefit

✅ **Mutual linking** — Frameworks link to your starters, you link back, everyone wins

✅ **SEO** — Your starters appear in "[Framework] integration examples" searches

---

## Quick Reference

| Starter | Priority | Status | Time | Value |
|---|---|---|---|---|
| hermes-mcp-bridge-starter | ⭐⭐⭐⭐⭐ | ⏳ Ready | 2-3h | Primary use case + proof of concept |
| mcp-agent-starter | ⭐⭐⭐⭐⭐ | ⏳ Ready | 2-3h | Can PR to official MCP repo |
| langchain-mcp-bridge-starter | ⭐⭐⭐⭐ | ⏳ Plan | 1-2h | Largest framework |
| langgraph-mcp-bridge-starter | ⭐⭐⭐⭐ | ⏳ Plan | 1-2h | Growing fast |
| autogen-mcp-bridge-starter | ⭐⭐⭐⭐ | ⏳ Plan | 1-2h | Microsoft backing |
| crewai-mcp-bridge-starter | ⭐⭐⭐ | ⏳ Plan | 1-2h | Already familiar |
| n8n-mcp-bridge-starter | ⭐⭐⭐ | ⏳ Plan | 1-2h | Workflow angle |

---

## Next Steps

**Start with hermes-mcp-bridge-starter:**

1. Create repo locally
2. Add files from templates above
3. Test end-to-end (Hermes → bridge → Claude Code)
4. Push to GitHub
5. Update main bridge README.md to link to it
6. Reference starter in all Hermes-related outreach (issues, PRs, etc.)

---

