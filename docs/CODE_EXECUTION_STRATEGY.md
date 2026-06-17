# Code Execution Strategy for Agent Frameworks

## Overview

When agent frameworks generate and execute code in production, teams face critical decisions: *Where does the code run? What can it access? When does it timeout? How do you audit it?*

This guide documents production patterns for safe, auditable code execution in agent workflows. It's not prescriptive — it maps the decision space and shows three validated approaches.

---

## Decision Tree

Every code execution strategy balances **safety** (isolation), **power** (context access), and **simplicity** (setup overhead).

```
START: Agent generates code
  │
  ├─ Q1: Where should code run?
  │   ├─ Cloud sandbox (E2B, Replit) → Skip to "Cloud Sandbox"
  │   ├─ Isolated local environment → Skip to "Venv Boundary"
  │   └─ Local with full context → Skip to "Local Subprocess"
  │
  ├─ Q2: What can code access?
  │   ├─ Scoped workspace only → Venv Boundary
  │   ├─ Full repo + shell → Local Subprocess
  │   └─ Managed environment → Cloud Sandbox
  │
  ├─ Q3: Who validates generated code?
  │   ├─ Framework (automatic) → Skip validation
  │   ├─ Second agent (reviewer) → Add review step before execution
  │   └─ Human (manual) → Add approval gate
  │
  └─ Q4: How do you recover from failures?
      ├─ Logs only → Basic recovery
      ├─ Logs + checkpoints → Resumable operations
      └─ Logs + filesystem snapshots → Full rollback
```

---

## Three Reference Implementations

### Option A: Cloud Sandbox (E2B, Replit)

**How it works:**
```
Agent generates code → E2B API call → Temporary sandbox → Return result
```

**Pros:**
- ✅ Managed security (no local setup)
- ✅ Inherent isolation (different process, timeout enforced)
- ✅ Minimal audit burden (provider handles cleanup)

**Cons:**
- ❌ Per-execution costs ($0.01-$0.10 per run)
- ❌ Network latency (50-500ms overhead)
- ❌ API key management (separate billing, rate limits)
- ❌ No local context (can't access your repos, env vars)

**Best for:**
- Teams with budget for managed execution
- Workflows without repo access requirements
- Cloud-first deployments

**Implementation (reference):**
```python
from crewai import Agent, Task, Crew
from e2b import Sandbox

code_executor = Sandbox()

executor_agent = Agent(
    name="Code Executor",
    tools=[CodeExecutionTool(sandbox=code_executor)]
)

crew = Crew(agents=[generator, reviewer, executor_agent])
crew.kickoff()
```

---

### Option B: Venv Boundary (SwarmAI Pattern)

**How it works:**
```
Agent generates code → Save to workspace → Create venv → Run script → Capture output → Cleanup venv
```

**Pros:**
- ✅ Maximum isolation (fresh venv per task, can't corrupt agent state)
- ✅ Reproducibility (exact code logged + deps declared)
- ✅ Explicit dependency management (know what's installed)
- ✅ Local execution (no API costs)

**Cons:**
- ❌ More setup (venv creation, dependency installation)
- ❌ No repo context (scoped workspace only)
- ❌ Slower (venv creation overhead)
- ❌ Requires explicit file sharing (need to pass data in/out)

**Best for:**
- Teams paranoid about state bleed
- Workflows with untrusted generated code
- Scenarios requiring explicit dependency control

**Architecture (from production):**
```
workspace/
  skill_module/
    __init__.py
    requirements.txt
    generated_code.py
  artifacts/
    generated_code/            # Audit log
    state_snapshot.json       # Before execution
  venv/                        # Isolated environment
  .artifacts/log.jsonl        # Execution log
```

**Implementation (reference):**
```python
from crewai import Agent, Task, Crew
from venv_executor import VenvBoundary

executor = VenvBoundary(
    workspace_dir="/tmp/crew_workspace",
    allowed_network=["github.com", "api.example.com"],
    timeout_seconds=300,
    audit_dir=".artifacts/generated_code"
)

generator = Agent(name="Code Generator", ...)
reviewer = Agent(name="Code Reviewer", ...)
executor_agent = Agent(
    name="Executor",
    code_executor=executor
)

crew = Crew(agents=[generator, reviewer, executor_agent])
result = crew.kickoff()
```

---

### Option C: Local Subprocess (cowork-to-code-bridge Pattern)

**How it works:**
```
Agent generates code → Queue task → Escalate to Claude Code → Agent executes → Return result
```

**Pros:**
- ✅ Full context access (your repos, shell, environment, secrets)
- ✅ Simplest setup (daemon + subprocess)
- ✅ No API costs (uses Claude subscription you already have)
- ✅ Persistent context (agent remembers prior tasks)
- ✅ Production-tested (Hermes, Open Claw, Crew.ai)

**Cons:**
- ❌ Less isolation (full local environment)
- ❌ Requires daemon running (background process management)
- ❌ State carryover (could be feature or bug)

**Best for:**
- Complex workflows needing repo access
- Teams valuing simplicity over isolation
- Multi-step tasks requiring context carryover
- Leveraging existing Claude subscription

**Architecture (from production):**
```
~/.cowork-to-code-bridge/
  queue/
    op_bridge_1718556000_a4f2c1_01.json       # Incoming task
  operations/
    bridge_1718556000_a4f2c1_01.json          # State + checkpoint
    bridge_1718556000_a4f2c1_01.log           # Live progress
  results/
    bridge_1718556000_a4f2c1_01.json          # Final result (cached)
  journal.log                                  # All operations (audit)
```

**Implementation (reference):**
```python
from crewai import Agent, Task, Crew
from cowork_to_code_bridge import CodeExecutionBridge

executor = CodeExecutionBridge(
    bridge_root="~/.cowork-to-code-bridge",
    timeout_seconds=600,
    poll_interval=1.0
)

generator = Agent(
    name="Code Generator",
    tools=[executor.escalate_tool()]
)

reviewer = Agent(
    name="Code Reviewer",
    tools=[executor.escalate_tool()]
)

executor_agent = Agent(
    name="Executor",
    tools=[executor.escalate_tool()]
)

crew = Crew(
    agents=[generator, reviewer, executor_agent],
    verbose=True
)

result = crew.kickoff()
```

---

## Example Crew: Generator → Reviewer → Executor

This pattern validates generated code before execution:

```python
from crewai import Agent, Task, Crew

# Choose execution strategy (swap as needed)
# executor = CloudSandbox(api_key="...")
# executor = VenvBoundary(workspace_dir="/tmp/crew")
executor = CodeExecutionBridge()

# Agent 1: Generate code
generator = Agent(
    role="Code Generator",
    goal="Generate Python code that solves the problem",
    backstory="Expert Python developer with deep knowledge of best practices.",
    tools=[executor.escalate_tool()]
)

generate_task = Task(
    description="""
    Generate a Python script that:
    1. Reads data from input.json
    2. Transforms it according to the spec
    3. Writes output to output.json
    4. Returns a summary of what was processed
    
    Save the code as a complete, runnable script.
    """,
    agent=generator,
    expected_output="Complete Python script as code block"
)

# Agent 2: Review code
reviewer = Agent(
    role="Code Reviewer",
    goal="Ensure generated code is safe, efficient, and correct",
    backstory="Senior engineer with 15 years of experience in production systems.",
    tools=[executor.escalate_tool()]
)

review_task = Task(
    description="""
    Review the generated Python script for:
    1. Security issues (e.g., injection, unsafe file operations)
    2. Performance issues (e.g., N² loops, memory leaks)
    3. Error handling (does it fail gracefully?)
    4. Code style (follows PEP 8)
    
    Provide feedback or approve for execution.
    """,
    agent=reviewer,
    context=[generate_task],
    expected_output="Approval + feedback (or rejection with reasons)"
)

# Agent 3: Execute code
executor_agent = Agent(
    role="Code Executor",
    goal="Execute reviewed code safely and capture results",
    backstory="DevOps engineer skilled in safe execution, logging, and error recovery.",
    tools=[executor.escalate_tool()]
)

execute_task = Task(
    description="""
    Execute the reviewed Python script:
    1. Verify input.json exists
    2. Run the script (timeout 300 seconds)
    3. Capture stdout/stderr
    4. Verify output.json was created
    5. Log execution details
    
    Return execution results + captured output.
    """,
    agent=executor_agent,
    context=[generate_task, review_task],
    expected_output="Execution result + metrics (success/failure, runtime, output summary)"
)

# Orchestrate
crew = Crew(
    agents=[generator, reviewer, executor_agent],
    tasks=[generate_task, review_task, execute_task],
    verbose=True
)

result = crew.kickoff()
print(f"Final result: {result}")
```

---

## Production Checklist

Before shipping an agent that executes code, verify:

### Logging & Auditability
- [ ] All generated code is logged **before execution** (audit trail)
- [ ] Execution logs include: timestamp, code, env state, stdout, stderr, exit code
- [ ] Logs are searchable and persisted (not ephemeral)
- [ ] You can trace: agent decision → generated code → execution result

### Safety
- [ ] Timeout enforced (no infinite loops)
- [ ] Resource limits set (CPU, memory, disk)
- [ ] Filesystem access scoped (no `rm -rf /`)
- [ ] Network access whitelisted (explicit allow-list, not default-allow)
- [ ] Secrets are not logged (redact API keys, tokens)

### Error Recovery
- [ ] Failed tasks don't corrupt agent state
- [ ] Partial progress is checkpointed (resumable)
- [ ] Rollback is possible (filesystem snapshots or transaction logs)
- [ ] Retry is safe (idempotent operations)

### Monitoring
- [ ] Execution metrics captured (latency, success rate, resource usage)
- [ ] Alerts on anomalies (timeout, crash, resource exhaustion)
- [ ] Dashboard shows: tasks pending, in-progress, completed, failed
- [ ] Historical data retained for analysis

### Documentation
- [ ] Decision: why this strategy (safety vs simplicity trade-off)?
- [ ] Configuration: timeout, resource limits, allow-list, audit path
- [ ] Runbook: how to debug failed executions
- [ ] SLA: expected latency, uptime, failure rate

---

## Resource Limits Reference

Tune these based on your threat model:

### Timeouts
```
Code generation:    300s (5 min)     | Agent thinking time
Code execution:     600s (10 min)    | Actual task runtime
Full workflow:      1800s (30 min)   | End-to-end SLA
```

### Subprocess Isolation (Local Subprocess)
```
Memory:  512MB (code gen),  2GB (complex tasks)
Disk:    100MB temp workspace, cleanup after
CPU:     No limit (system available)
Network: Allow-list only
```

### Venv Isolation (Venv Boundary)
```
Memory:  Limited by venv creation (usually <100MB per)
Disk:    Scoped workspace (user-configurable)
CPU:     No limit (system available)
Network: Allow-list only
```

### Cloud Sandbox (E2B, etc.)
```
Memory:  Configured per provider (usually 512MB-2GB)
Disk:    Configured per provider (usually 100MB-5GB)
CPU:     Shared (burstable)
Network: Configurable per provider
```

---

## Decision Matrix

| Dimension | Cloud Sandbox | Venv Boundary | Local Subprocess |
|---|---|---|---|
| **Setup complexity** | Low | Medium | Low |
| **Isolation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Context access** | ❌ None | ⚠️ Scoped | ✅ Full |
| **Cost per execution** | $$$ | Free | Free |
| **Latency** | 50-500ms | 500ms-2s | 10-100ms |
| **Production maturity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Best for** | Cloud teams | Security-first | Context-heavy |

---

## Further Reading

- **[STATEFUL_OPERATION_PATTERN.md](./STATEFUL_OPERATION_PATTERN.md)** — Async operation model for long-running tasks
- **[MCP_SERVER_IMPLEMENTATION.md](./MCP_SERVER_IMPLEMENTATION.md)** — MCP server architecture
- **[EXTERNAL_AGENT_INTEGRATION.md](./EXTERNAL_AGENT_INTEGRATION.md)** — Integration with Hermes, Open Claw, Crew.ai

---

## Community References

- **SwarmAI** (venv boundary pattern) — https://github.com/xg-gh-25/SwarmAI
- **E2B** (cloud sandbox) — https://e2b.dev
- **cowork-to-code-bridge** (local subprocess) — https://github.com/abhinaykrupa/cowork-to-code-bridge

