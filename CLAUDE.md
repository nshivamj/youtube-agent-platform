# YouTube Agent Platform — Claude Context

Full codebase reference so Claude can skip re-exploration and jump straight to any task.

---

## What This Is

A multi-agent platform built on **Google ADK** (Agent Development Kit).
Agents collaborate in typed workflows to analyse YouTube watch history and run
entitlement control tests.  A `coordinator_agent` routes user requests to the
correct workflow via the `WorkflowRegistry`.

**Run it:**
```bash
python main.py              # starts ADK web UI at http://localhost:8080
adk web                     # ADK CLI — picks up root_agent from main.py
```

---

## Canonical Directory Layout

```
youtube-agent-platform/
│
├── main.py                         # Entry point — imports workflows, builds coordinator,
│                                   # exposes root_agent for adk web CLI
│
├── agents/                         # Agent definitions (Python, not YAML)
│   ├── coordinator_agent.py        # Routes to workflows via WorkflowRegistry
│   ├── planner_agent.py            # Decomposes complex tasks → ExecutionPlan
│   ├── analyzer_agent.py           # YouTube history analysis → AnalyzerOutput
│   ├── insights_agent.py           # Recommendations from analysis → InsightsOutput
│   ├── control_planner_agent.py    # Creates ControlTestPlan
│   ├── control_reviewer_agent.py   # 5-pass peer reviewer of plans
│   ├── control_executor_agent.py   # Runs check_user_entitlements tool
│   └── control_reporter_agent.py   # Produces ControlTestSummary report
│
├── workflows/                      # ADK workflow compositions (self-register)
│   ├── youtube_workflow.py         # SequentialAgent: analyzer → insights
│   └── control_testing_workflow.py # SequentialAgent: planner → loop-reviewer → executor → reporter
│
├── core/
│   ├── schemas/                    # Pydantic output schemas
│   │   ├── __init__.py             # Re-exports everything; use `from core.schemas import X`
│   │   ├── youtube.py              # VideoItem, BingeSession, AnalyzerOutput, InsightsOutput, ReportOutput
│   │   ├── planning.py             # Step, ExecutionPlan
│   │   ├── control_testing.py      # ControlTestPlan, ControlTestResult, ControlTestSummary
│   │   └── approval.py             # ApprovalRequest, ApprovalResponse, ApprovalDecision
│   └── session/                    # Pluggable session backend (swap without touching runtime)
│       ├── __init__.py             # Exports: SessionManager, InMemoryBackend, session_manager singleton
│       ├── base.py                 # AbstractSessionBackend — the contract all backends implement
│       ├── manager.py              # SessionManager: open/close/write/read/all + adk_service property
│       └── backends/
│           └── inmemory.py         # InMemoryBackend — wraps ADK InMemorySessionService
│
├── framework/
│   ├── workflow_registry.py        # WorkflowRegistry singleton — workflows self-register here
│   ├── execution_context.py        # ExecutionContext dataclass (run_id, session_id, user_id, ...)
│   ├── factory.py                  # Factory — builds agents/workflows from YAML (agent_configs/)
│   ├── callbacks/
│   │   ├── base_callback.py        # BaseCallback ABC — override only what you need
│   │   ├── logging_callback.py     # OOP: logs agent/tool events (used by CallbackComposer)
│   │   ├── tracing_callback.py     # OOP: timing traces per agent (used by CallbackComposer)
│   │   ├── narration_callback.py   # OOP: injects per-agent narration style into LLM calls
│   │   ├── approval_callback.py    # OOP: detects approval signals in agent text
│   │   ├── risk_callback.py        # OOP: blocks high-risk tool calls
│   │   ├── entitlement_callback.py # OOP: enforces AGENT_TOOL_POLICY table
│   │   ├── composer.py             # CallbackComposer + governance_composer + SHARED_REGISTRY
│   │   ├── before_agent_cb.py      # Functional: ALLOWED_AGENTS gate + session state injection
│   │   ├── after_agent_cb.py       # Functional: checkpoint + validation error logging
│   │   ├── logging_cb.py           # Functional: logs tool outcome to tracker
│   │   ├── narration_cb.py         # Functional: narration for YAML-defined agents (gitlab)
│   │   └── approval_cb.py          # Functional: gates write tools behind AUTO_APPROVE check
│   ├── tools/
│   │   ├── resolver.py             # ToolResolver (resolver singleton) + functional resolve()
│   │   ├── base_tool.py            # BaseTool ABC for local/mcp tool wrappers
│   │   ├── registry.py             # Tool registry interface (used by factory)
│   │   ├── local_registry.py       # Local tool storage: register()/get()/list_all()
│   │   ├── mcp_registry.py         # MCP tool storage (same API)
│   │   └── local/
│   │       ├── youtube_local.py    # Tools: get_watch_summary, get_shorts_ratio, get_top_channels,
│   │       │                       #        get_watch_by_hour, get_binge_sessions, save_report
│   │       ├── file_local.py       # Tools: file read/write/delete
│   │       └── entitlement_local.py# Tools: check_user_entitlements (simulated access matrix)
│   ├── approval/
│   │   └── approval_handler.py     # ApprovalHandler — asyncio.Future-based pause-for-human
│   └── runtime/
│       ├── __init__.py
│       └── agent_runtime.py        # AgentRuntime: wraps ADK Runner, streams events, dispatches
│                                   # to CallbackComposer. Singletons: runtime, control_testing_runtime
│
├── agent_configs/                  # YAML configs for factory-built agents (gitlab pattern)
│   ├── coordinator_agent/          # coordinator_agent.yaml + schemas/
│   └── gitlab_agent/               # gitlab_agent.yaml + callbacks/ + schemas/ + transformers/
│
├── workflow_configs/               # YAML configs for factory-built workflows
│   └── gitlab_workflow/            # gitlab_workflow.yaml + callbacks/ + transformers/
│
├── tools/
│   └── local/
│       └── gitlab_local.py         # GitLab API tools (registered via factory)
│
├── services/
│   ├── llm_service.py              # LLMService.get_model(agent_name) — env-var model resolution
│   └── api_service.py              # APIService — shared async httpx client with retry
│
├── observability/
│   └── tracker.py                  # ObservabilityTracker (BaseCallback) + _Tracker singleton
│                                   # Writes JSONL to logs/ and reports/traces/
│
├── mcp_servers/
│   └── github/
│       ├── server.py               # FastMCP GitHub server (repos, issues, PRs, commits, search)
│       ├── github_client.py        # GitHubClient — REST API wrapper
│       └── logger.py               # Logging util for MCP server
│
├── run_mcp_github.py               # Script to start the GitHub MCP server
├── requirements.txt                # google-adk, google-genai, fastmcp, pydantic, python-dotenv, httpx, mcp, pyyaml
├── .env                            # Local secrets (not committed)
└── .env.example                    # Template
```

---

## Key Architecture Patterns

### 1. Agent + Workflow Pattern (primary — used by main.py)

Agents are plain Python files in `agents/`. Workflows compose them in `workflows/` and
**self-register** into `WorkflowRegistry`. `main.py` just imports the workflow modules
to trigger registration, then calls `build_coordinator_agent()`.

```
main.py
  └─ import workflows.youtube_workflow        # triggers workflow_registry.register(...)
  └─ import workflows.control_testing_workflow
  └─ build_coordinator_agent()               # reads workflow_registry, builds LlmAgent
  └─ root_agent = coordinator                # picked up by `adk web`
```

Adding a new workflow: create `workflows/my_workflow.py`, call `workflow_registry.register(...)`,
add one import line in `main.py`. No other changes needed.

### 2. YAML Factory Pattern (secondary — used for gitlab agent)

`framework/factory.py` reads `agent_configs/<id>/<id>.yaml` and `workflow_configs/<id>/<id>.yaml`
to build ADK agents. Used for external-integration agents (gitlab). Not used by the primary runtime.

### 3. Tool Resolution

Agents declare their tool surface with `resolver.declare(agent_name, tools=[...])`.
At build time `resolver.resolve(agent_name)` returns the actual callables.
Tool implementations live in `framework/tools/local/`.

```python
# In an agent file:
resolver.declare("analyzer_agent", tools=["get_watch_summary", "get_shorts_ratio", ...])
tools = resolver.resolve("analyzer_agent")  # called in build_*_agent()
```

### 4. Session Management

`core/session/` is the **only** session layer. Do not create another one.

```
AbstractSessionBackend  (core/session/base.py)
  └─ InMemoryBackend    (core/session/backends/inmemory.py)
        ↑ injected into
SessionManager          (core/session/manager.py)
  ├─ open(user_id, session_id) → ADK Session
  ├─ write(key, value) / read(key, default) / all()
  ├─ close()           ← clears keys after run
  └─ adk_service       ← pass to ADK Runner

# Singleton:
from core.session import session_manager
```

To swap backend (e.g. Redis): create `core/session/backends/redis.py` implementing
`AbstractSessionBackend`, then change `core/session/__init__.py` — nothing else changes.

### 5. Callbacks — Two Systems

| System | Files | Purpose |
|--------|-------|---------|
| **OOP** (`*_callback.py`) | `logging_callback.py`, `tracing_callback.py`, `narration_callback.py`, `approval_callback.py`, `risk_callback.py`, `entitlement_callback.py` | Used by `CallbackComposer` inside `AgentRuntime`; wrap ADK stream events |
| **Functional** (`*_cb.py`) | `before_agent_cb.py`, `after_agent_cb.py`, `logging_cb.py`, `narration_cb.py`, `approval_cb.py` | Passed directly to `LlmAgent(before_agent_callback=...)` by Factory |

These are **not duplicates** — they serve different integration points.

`composer.py` exports:
- `composer` — default (logging + tracing + narration + observability)
- `governance_composer` — adds approval + risk + entitlement
- `SHARED_REGISTRY` — name → functional callback, used by Factory's `compose()`

### 6. AgentRuntime vs adk web

- `AgentRuntime` (`framework/runtime/agent_runtime.py`) is for **programmatic execution**.
  It creates its own ADK `Runner`, streams events, and dispatches to `CallbackComposer`.
  Used when calling agents from code (e.g. tests, API, approval flows).
- `adk web` / `python main.py` use ADK's own web UI runner.
  ADK manages sessions itself; `AgentRuntime` is not involved.
  `root_agent = coordinator` in `main.py` is the discovery hook.

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `GOOGLE_API_KEY` | — | **Required.** Gemini API key |
| `MODEL` | `gemini-2.0-flash` | Global model for all agents |
| `MODEL_<AGENT_NAME_UPPER>` | — | Per-agent model override (e.g. `MODEL_ANALYZER_AGENT`) |
| `TOOL_MODE` | `local` | `local` or `mcp` — controls factory tool resolver |
| `ALLOWED_AGENTS` | `*` | Comma-separated agent whitelist, or `*` for all |
| `AUTO_APPROVE` | `false` | Set `true` to bypass approval gates |

---

## Schemas Quick Reference

All schemas are Pydantic models. Import from `core.schemas`:

```python
from core.schemas import (
    AnalyzerOutput, InsightsOutput, ReportOutput,   # youtube
    ExecutionPlan,                                   # planning
    ControlTestPlan, ControlTestResult,
    ControlTestSummary,                              # control testing
    ApprovalRequest, ApprovalResponse,               # approval flow
)
```

---

## What Has Been Removed (Do Not Recreate)

| Removed | Why |
|---------|-----|
| `session_manager.py` (root) | Duplicate — `core/session/` is canonical |
| `core/session_manager.py` | Duplicate — `core/session/` is canonical |
| `agents/basic_agent/`, `agents/github_agent/` | Auto-generated stubs; imported non-existent `app.agents.registry` |
| `agents-config/`, `workflows-config/` | Old YAML dirs; `agents/*.py` + `workflows/*.py` is canonical |
| `app/` (entire directory) | Old architecture — orchestrator, runner, MCP clients, tool loader |
| `scripts/generate_adk_agents.py` | Broken generator; agents are hand-written Python now |
| `local_tools/` | Old location; `framework/tools/` is canonical |
| `main_platform.py` | Conflicting factory-based entry point |
| `framework/runtime.py` (flat file) | Replaced by `framework/runtime/agent_runtime.py` |

---

## Common Tasks

**Add a new agent:**
1. Create `agents/my_agent.py` — define `build_my_agent()`, call `resolver.declare()`, export `my_agent = build_my_agent()`
2. Add tools to `framework/tools/local/` and register in the appropriate registry

**Add a new workflow:**
1. Create `workflows/my_workflow.py` — compose agents into a `SequentialAgent` or `LoopAgent`
2. Call `workflow_registry.register(name, workflow, description, triggers=[...])`
3. Add `import workflows.my_workflow` in `main.py`

**Add a new schema:**
1. Add Pydantic model to the appropriate file in `core/schemas/`
2. Re-export it in `core/schemas/__init__.py`

**Swap session backend:**
1. Create `core/session/backends/my_backend.py` implementing `AbstractSessionBackend`
2. Update `core/session/__init__.py`: `session_manager = SessionManager(backend=MyBackend())`

**Add a YAML-configured agent (factory pattern):**
1. Create `agent_configs/<id>/<id>.yaml` with `model`, `prompt`, `tools`, `callbacks` keys
2. Optionally add `agent_configs/<id>/callbacks/`, `schemas/`, `transformers/` subdirs
3. Use `Factory().create_agent("<id>")` to instantiate
