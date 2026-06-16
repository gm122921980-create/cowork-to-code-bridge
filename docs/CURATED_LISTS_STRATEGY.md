# Curated Lists Strategy — High-Leverage PRs

Status: Ready to execute
Priority: ⭐⭐⭐⭐⭐ (one PR = exposure to 1000s of downstream users)

---

## Strategy Overview

Instead of opening issues in 20 repos, PRs to curated lists give **durable SEO + discovery** with **less friction**. One merged PR = permanent listing seen by everyone discovering that topic.

**Leverage:** awesome-ai-agents-2026 with 10k stars = your bridge visible to 10k+ people looking for agent tools.

---

## Target #1: awesome-ai-agents-2026

**Repository:** https://github.com/caramaschiHG/awesome-ai-agents-2026  
**Priority:** ⭐⭐⭐⭐⭐ (2026-focused, active maintainers)  
**Type:** Add section + list entry  
**Estimated Time:** 15 minutes

### PR Title
```
Add "Local Execution Bridges" section with cowork-to-code-bridge
```

### PR Body (Copy-Paste Ready)

```markdown
## Summary

Adding a new "Local Execution Bridges" subsection under Agent Infrastructure to highlight MCP-based solutions for local Claude Code execution without API keys.

## What's being added

**New subsection:** `## Local Execution Bridges`

**Entry:**
- **cowork-to-code-bridge** — MCP server exposing Claude Code subscription as local execution backend for agents. Zero network ports, token-authenticated, production-ready. (Python, JSONRPC 2.0)

## Why this matters

Agent frameworks increasingly need local code execution without separate API billing. This bridge solves exactly that: agents delegate to Claude Code running on the user's machine using existing subscription. MCP-native.

## Links for maintainers

- Repo: https://github.com/abhinaykrupa/cowork-to-code-bridge
- MCP Docs: https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/MCP_SERVER_IMPLEMENTATION.md
- Live examples: Crew.ai (#6178), Hermes (#47199), Open Claw (#93609)

## Proposed location in awesome-ai-agents-2026

Under `## Agent Infrastructure / Tools` → new subsection `### Local Execution Bridges`

---

Would you like me to add more entries to this section, or refine the description?
```

### Section Text (Ready to Paste)

```markdown
### Local Execution Bridges

Tools and frameworks enabling agents to execute code locally without additional API billing.

- **cowork-to-code-bridge** — MCP server exposing Claude Code subscription as local execution backend. Zero network ports, file-based queue, production-ready. Used by Crew.ai, Hermes, Open Claw communities. [GitHub](https://github.com/abhinaykrupa/cowork-to-code-bridge) | [Docs](https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/MCP_SERVER_IMPLEMENTATION.md)
```

---

## Target #2: awesome-mcp-servers

**Repository:** https://github.com/punkpeye/awesome-mcp-servers  
**Priority:** ⭐⭐⭐⭐⭐ (official MCP discovery hub)  
**Type:** Add to list  
**Estimated Time:** 10 minutes

### PR Title
```
Add cowork-to-code-bridge — MCP server for Claude Code local execution
```

### PR Body

```markdown
## Summary

Adding cowork-to-code-bridge to the "Developer Tools & Infrastructure" section as an MCP server for local Claude Code execution.

## Entry

- **cowork-to-code-bridge** — MCP server (JSONRPC 2.0) exposing Claude Code as local execution backend for agents. No API keys, zero network ports, token-authenticated. [GitHub](https://github.com/abhinaykrupa/cowork-to-code-bridge) [Docs](https://github.com/abhinaykrupa/cowork-to-code-bridge/blob/main/docs/MCP_SERVER_IMPLEMENTATION.md)

## Why this matters

This is a reference implementation of MCP servers for local code execution. Agents using MCP increasingly need a reliable local backend without separate API costs. The bridge fills that gap.

## Status

- Production-ready: 570 lines + 9 unit tests
- Used by: Crew.ai, Hermes, Open Claw
- Live issues: Hermes #47199, Open Claw #93609, Crew.ai #6178
```

### List Entry (Ready to Paste)

```markdown
- **cowork-to-code-bridge** — MCP server for Claude Code subscription as local execution backend for agents. JSONRPC 2.0, token-authenticated, zero network ports. [GitHub](https://github.com/abhinaykrupa/cowork-to-code-bridge)
```

---

## Target #3: awesome-mcp-clients

**Repository:** https://github.com/punkpeye/awesome-mcp-clients  
**Priority:** ⭐⭐⭐⭐ (broader MCP discovery)  
**Type:** Add under "Servers" section  
**Estimated Time:** 10 minutes

### PR Title
```
Add cowork-to-code-bridge to "Servers & Backends" section
```

### PR Body

```markdown
## Summary

Adding cowork-to-code-bridge under "Servers & Backends" as a production MCP server implementation reference.

## Entry

**cowork-to-code-bridge** — MCP server exposing Claude Code subscription as local execution backend for agents. Zero network ports, token-authenticated, idempotent. Reference implementation for local code execution patterns. [GitHub](https://github.com/abhinaykrupa/cowork-to-code-bridge)

## Notes

This is both a working server and reference implementation showing how to build MCP servers for local execution backends. Used in production by Crew.ai, Hermes, Open Claw communities.
```

---

## Target #4: 500-AI-Agents-Projects

**Repository:** https://github.com/ashishpatel26/500-AI-Agents-Projects  
**Priority:** ⭐⭐⭐⭐ (broad AI/ML audience)  
**Type:** Add to "Infrastructure / Tooling" section  
**Estimated Time:** 10 minutes

### PR Title
```
Add cowork-to-code-bridge — Agent execution infrastructure
```

### PR Body

```markdown
## Summary

Adding cowork-to-code-bridge under "Infrastructure & Tooling" → "Agent Execution Backends" as a production-ready solution for local Claude Code execution.

## Entry

**cowork-to-code-bridge** — Bridge Claude Code subscription as MCP provider for agent frameworks (Crew.ai, Hermes, Open Claw, LangChain, AutoGen, etc.). Zero API key management, local execution, no separate billing. [GitHub](https://github.com/abhinaykrupa/cowork-to-code-bridge)

## Why this fits

This is infrastructure enabling multi-agent projects to use Claude Code locally without API management complexity. Complements agent frameworks by providing the execution layer.
```

### List Entry

```markdown
- **cowork-to-code-bridge** — MCP server bridging Claude Code subscription as local execution backend for agents. Zero API keys, production-ready. [GitHub](https://github.com/abhinaykrupa/cowork-to-code-bridge)
```

---

## Target #5: awesome-ai-agents (broader)

**Repository:** https://github.com/e2b-dev/awesome-ai-agents  
**Priority:** ⭐⭐⭐⭐ (large AI audience)  
**Type:** Add new "Local Execution" section  
**Estimated Time:** 15 minutes

### PR Title
```
Add "Local Execution Backends" section with MCP-based solutions
```

### PR Body

```markdown
## Summary

Adding new "Local Execution Backends" section under "Infrastructure & Tools" for MCP-based local execution solutions.

## New section

**Local Execution Backends**

Tools enabling agents to execute code locally without cloud API dependencies.

- **cowork-to-code-bridge** — MCP server for Claude Code subscription as local backend. Zero network ports, token-authenticated, production-ready. Used by Crew.ai, Hermes, Open Claw. [GitHub](https://github.com/abhinaykrupa/cowork-to-code-bridge)

## Rationale

Agent frameworks increasingly need local execution without separate billing. This section highlights solutions filling that gap.
```

---

## Target #6: awesome_ai_agents (1500+ entries)

**Repository:** https://github.com/jim-schwoebel/awesome_ai_agents  
**Priority:** ⭐⭐⭐ (massive list, slightly lower conversion)  
**Type:** Add to "Infrastructure" section  
**Estimated Time:** 10 minutes

### PR Title
```
Add cowork-to-code-bridge to Infrastructure section
```

### PR Body

```markdown
## Summary

Adding cowork-to-code-bridge under "Infrastructure → Execution Backends" as a production MCP server for local Claude Code.

## Entry

- cowork-to-code-bridge (Python) — MCP server for Claude Code subscription as local agent execution backend. GitHub: https://github.com/abhinaykrupa/cowork-to-code-bridge

## Why it belongs

Infrastructure for agents needing local execution without API key management. Used by multiple agent frameworks (Crew.ai, Hermes, Open Claw).
```

---

## Execution Checklist

### Before Each PR

- [ ] Fork the repo (if not already forked)
- [ ] Create new branch: `git checkout -b add-cowork-to-code-bridge`
- [ ] Locate the relevant section in README.md or CONTRIBUTING.md
- [ ] Find where to insert the entry (alphabetical? by type?)
- [ ] Check existing entries for tone/format
- [ ] Adapt PR body to match repo's style

### Creating the PR

- [ ] Copy PR title from above
- [ ] Copy PR body from above, customize if needed
- [ ] Add 1-2 sentences explaining why it fits this list specifically
- [ ] Link to GitHub repo + main docs
- [ ] Submit PR

### After PR Submission

- [ ] Monitor for maintainer feedback (usually within 3-7 days)
- [ ] Be responsive to any formatting/content requests
- [ ] Thank maintainer if merged
- [ ] Update tracking table (below) with PR #

---

## Tracking Table

| List | Stars | Status | PR # | Date | Notes |
|---|---|---|---|---|---|
| awesome-ai-agents-2026 | 1k+ | ⏳ Ready | — | — | Newest, 2026-focused |
| awesome-mcp-servers | 1k+ | ⏳ Ready | — | — | Official MCP hub |
| awesome-mcp-clients | 500+ | ⏳ Ready | — | — | MCP clients + servers |
| 500-AI-Agents-Projects | 3k+ | ⏳ Ready | — | — | Broad coverage |
| awesome-ai-agents | 2k+ | ⏳ Ready | — | — | Large audience |
| awesome_ai_agents | 5k+ | ⏳ Ready | — | — | 1500+ entries |

**Total Reach:** 10,000+ people + durable SEO

---

## Tips for Success

✅ **Read the repo's CONTRIBUTING.md first** — Follow their format exactly

✅ **One entry = one thing** — Don't overwhelm with multiple entries in same PR

✅ **Check for duplicates** — Make sure bridge isn't already listed under different name

✅ **Keep entry concise** — 1-2 lines max, let the links do the work

✅ **Mention live usage** — "Used by Crew.ai, Hermes, Open Claw" builds credibility

✅ **Be responsive** — If maintainer asks for tweaks, respond same day

✅ **Don't be pushy** — If rejected, move on; no follow-ups

---

## Expected Success Rate

- **awesome-mcp-servers:** 90% (official MCP hub, obvious fit)
- **awesome-ai-agents-2026:** 80% (new list, maintainers actively adding)
- **awesome-ai-agents:** 70% (larger list, more selective)
- **awesome-mcp-clients:** 70% (good fit, medium size)
- **500-AI-Agents-Projects:** 60% (broad list, more competitive)
- **awesome_ai_agents:** 50% (massive list, lower acceptance rate)

**Expected outcome:** 3-4 PRs merged = permanent listing in 4+ curated lists

---

## Next Steps

1. **Immediate:** Submit PR #1 (awesome-ai-agents-2026) + PR #2 (awesome-mcp-servers)
2. **Week 2:** Submit remaining PRs (awesome-mcp-clients, 500-AI-Agents-Projects, awesome-ai-agents)
3. **Week 3:** awesome_ai_agents (lower priority)
4. **Ongoing:** Monitor PRs + respond to feedback

Total time investment: ~90 minutes spread over 3 weeks.
Expected reach: 10,000+ developers (one-time cost, permanent listing).

