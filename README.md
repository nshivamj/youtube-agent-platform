# ADK Agent Platform

A production-ready starter project for building reusable AI agents with **Google ADK** and **Gemini 2.5 Flash**.

---

## Project Structure

```
.
├── agents/             # ADK agent definitions
│   └── basic_agent.py  # Minimal Gemini agent
├── agent_platform/     # Reusable infrastructure
│   ├── config.py       # Environment-based configuration
│   ├── memory.py       # In-process key-value store (swap for Redis/Firestore)
│   └── runner.py       # Synchronous wrapper around ADK Runner
├── tools/              # Future MCP or local tool wrappers
├── data/               # Input files placeholder
├── main.py             # Entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Clone & enter the project

```bash
git clone <repo-url>
cd youtube-agent-platform
```

### 2. Create & activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Open .env and set GOOGLE_API_KEY
```

Get a free API key at <https://aistudio.google.com/app/apikey>.

### 5. Run

```bash
python main.py
# or with a custom prompt:
python main.py "Explain what an AI agent is in two sentences"
```

---

## Extending the Platform

| Goal | Where to add code |
|---|---|
| New agent | `agents/my_agent.py` → `create_my_agent()` |
| New tool | `tools/my_tool.py` → pass to `Agent(tools=[...])` |
| Persistent memory | Replace `InMemoryStore` in `agent_platform/memory.py` |
| New env var | Add to `agent_platform/config.py` and `.env.example` |

---

## Requirements

- Python 3.10+
- `GOOGLE_API_KEY` with Gemini API access
