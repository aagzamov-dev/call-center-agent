# Backend & Agent Architecture Overview

This project is a high-performance **Incident AI Agent** system. It uses **FastAPI** for the web layer, **LangGraph** for multi-step agent reasoning, and **SQLite** for lightweight persistence.

---

## 🏗️ Core Architecture

- **Web Layer**: FastAPI + Pydantic + WebSockets.
- **Agent Layer**: LangGraph `StateGraph`. Unlike a simple "prompt + LLM", this is a stateful workflow that can loop, call tools, and verify findings.
- **Tool Layer**: 10 deterministic tools (some real, some stubbed) providing logs, metrics, topology, etc.
- **Persistence**: SQLite (2-table design: `incidents` for state, `events` for the timeline).

---

## 📂 File-by-File Breakdown

### `api/app/core/`
- **`config.py`**: Loads environment variables (`.env`).
- **`event_bus.py`**: In-memory Pub/Sub. When a new event is saved to the DB, it's broadcasted to active WebSockets.

### `api/app/db/`
- **`engine.py`**: Async SQLAlchemy setup.
- **`models.py`**: Database schema. `Event` table is the "Source of Truth" for the timeline history.

### `api/app/services/`
- **`incident_service.py`**: Handles all CRUD. Every action (alert, message, ticket) is saved as an `Event`.
- **`audio_service.py`**: Uses `whisper-1` (STT) to transcribe voice recordings into text. Cheap at $0.006/min.

### `api/app/tools/`
- **`registry.py`**: The "Brain" of tools. Maps tool names to implementations and wraps them for LangChain.
- **`alerts.py`, `metrics.py`, `logs.py`, etc.**: Specific tools providing the agent with data.

### `api/app/agent/`
- **`state.py`**: Defines what the agent "remembers" during its run (conversation history, evidence).
- **`prompts.py`**: The "NOC Operator" personality and context builder.
- **`nodes.py`**: Individual steps in the agent's brain (Gather → Investigate → Plan).
- **`graph.py`**: The workflow map. Connects nodes with logical edges.

---

## 🤖 How the Agent Works

When you call `POST /api/incidents/{id}/agent/step`, the **LangGraph** starts:

1.  **START** → `gather_context`: Automatically pulls incident data, recent timeline, service topology, and relevant runbooks. No AI cost yet.
2.  **`investigate` (LLM)**: The LLM looks at the context and decides which tools to call (e.g., "I see a disk alert, let me run `df -h`").
3.  **`execute_tools`**: The system runs the requested tools and feeds the technical output back to the LLM.
4.  **Loop**: Steps 2 & 3 repeat until the LLM has enough evidence.
5.  **`produce_plan`**: The LLM generates a **Structured JSON Plan** (hypotheses, evidence summary, and specific actions).
6.  **`execute_actions`**: The system validates the plan against `policy.py`.
    - **Safe** (e.g., Create Ticket, Send Chat): Executed automatically.
    - **Risky** (e.g., Make Voice Call, Resolve): Marked as "Needs Approval".
7.  **END**: High-fidelity events are created on the timeline for you to see.

---

## 💬 How to Interact

### What can the Agent do?
- **Analyze**: Metrics, logs, connection errors, and firewall rules.
- **Communicate**: Email, Chat (Slack-like), and Voice (upload audio → auto-transcribed → fed to agent).
- **Manage**: Create/Update tickets, change severity, resolve incidents.

### Questions/Hints to give the Agent:
- *"Check the database connections specifically; we had a similar issue last week."*
- *"Does the firewall have any recent deny rules for this host?"*
- *"Don't create a ticket yet, just gather evidence."*
- *"This is a production emergency, escalate and notify on-call immediately."*
