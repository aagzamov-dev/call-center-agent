# AI Support Node Agent: Backend Logic Explained

This document explains exactly how the backend agent (the brain of the chat and voice support) works step-by-step. If you aren't familiar with Python, think of this as a recipe book. Every time a user sends a message, it gets cooked through several files in a specific order before returning a response.

---

## 🏗️ 1. The Core Architecture (LangGraph)

The AI agent is built using a tool called **LangGraph**. Think of LangGraph as a flow chart or a pipeline. Instead of having one massive AI prompt, we break the AI's job into **Nodes** (steps).

The nodes in our architecture are:
1. `triage`: Read the user's message and classify intent (chitchat, rag_needed, resolve, escalate, etc.)
2. `retrieval`: Search the Knowledge Base (RAG) via ChromaDB for relevant articles.
3. `tool_execution`: Run database queries if the user asks about their specific account/ticket data.
4. `evaluate_context`: Rate whether the retrieved context is good enough to answer.
5. `draft_resolution`: Write the actual reply using the main LLM, guided by context and general IT knowledge.
6. `ticket_action`: Classify what ticket action to take (create, update, resolve, escalate).
7. `escalate`: Handle frustrated users / low-confidence scenarios.
8. `handle_resolution`: Auto-close ticket when user says "thanks" or confirms fix.
9. `observe`: Silent mode when a human admin is already helping.
10. `quick_respond`: Fast chitchat responses without KB search.

### The Flow (`app/agent/graph.py`)

```
User Message
    ↓
  triage (gpt-4.1-nano — fast classifier)
    ↓ (conditional routing by intent)
    ├─ chitchat → quick_respond → END
    ├─ resolve  → handle_resolution → END  ← [OPTIMIZED: skips ticket_action LLM]
    ├─ observe  → observe → END
    ├─ escalate → escalate → ticket_action → END
    ├─ db_query → tool_execution → evaluate_context → ...
    └─ rag_needed → retrieval → evaluate_context
                                      ↓ (conditional)
                                      ├─ confidence < 0.4 → escalate → ticket_action → END
                                      └─ confidence >= 0.4 → draft_resolution → ticket_action → END
```

When you call `run_support_agent(user_message="My VPN is broken!")`, it triggers this flowchart from start to finish.

---

## 🧠 2. The Nodes (The actual logic steps)

The file `app/agent/nodes.py` contains the code that runs when the flowchart hits a specific node.

### Two LLM Models (Speed Optimization)

- **Fast LLM** (`gpt-4.1-nano`): Used for triage, evaluation, and classification. Ultra-fast, ultra-cheap.
- **Main LLM** (`gpt-4.1-mini`): Used for drafting responses. Smarter, still fast.

### Step 1: The `triage` Node

Classifies the user's message into an intent using the fast model. Extracts sentiment and metadata filters (OS, device, etc.).

**Intents**: `chitchat`, `rag_needed`, `db_query`, `escalate`, `observe`, `resolve`

**Fast path**: If admin is already in the conversation history, immediately returns `observe` intent (no LLM call needed).

### Step 2: The `retrieval` Node

Searches ChromaDB Knowledge Base for relevant articles using semantic vector search.

### Step 3: The `evaluate_context` Node

Rates context confidence from 0.0 to 1.0. If below `EVAL_THRESHOLD` (default 0.4, configurable via `.env`), the flow escalates to a human.

### Step 4: The `draft_resolution` Node

**Key behavior** (optimized):
- **General IT questions** (slow PC, browser cache, password tips): Gives 2-3 simple hints from general knowledge + "If not resolved, Admin will follow up."
- **Company-specific questions** (internal systems, policies): Answers ONLY from KB context. If no match, says "I don't have that info, Admin will follow up."

### Step 5: The `ticket_action` Node

Determines ticket CRUD action: `create`, `update`, `resolve`, `escalate`, or `none`.

### Step 6: The `handle_resolution` Node

**Optimized**: When user says "thanks", "fixed", "worked", etc., this node:
1. Sends a friendly goodbye message
2. Sets `ticket_action = {action: "resolve"}` directly
3. Goes straight to `END` — **no extra LLM call** for classification

### Step 7: The `observe` Node

Silent mode. When admin is already helping, the agent steps back. If user says thanks while admin is active, responds politely.

### Step 8: The `quick_respond` Node

Fast chitchat responses using the fast model. No KB search, no ticket creation.

---

## ✉️ 3. The API Router Gateway (`app/routers/chat.py`)

When the Frontend React app sends an HTTP `POST` request to `/api/chat`, this file catches it.

1. Duplicate detection — checks if a similar open ticket already exists (using embeddings).
2. Loads chat history from DB if continuing an existing ticket.
3. Runs the LangGraph agent pipeline.
4. Creates/updates ticket in DB based on the agent's decision.
5. Saves messages and broadcasts via WebSocket.

---

## 📡 4. WebSockets Broadcasting (`app/core/websockets.py` and `app/routers/ws.py`)

A WebSocket is a permanent pipeline between the Frontend browser and the Python backend.

- `ConnectionManager` holds a dictionary: `{'TKT-123': [User A's Browser, Admin B's Browser]}`.
- `broadcast_to_ticket('TKT-123', new_message)` fires JSON to all connected browsers instantly.
- Supports `new_message`, `ticket_update`, and `agent_status` event types.

---

## 📚 5. RAG (Knowledge Base Search) (`app/services/rag_service.py`)

RAG = **Retrieval-Augmented Generation**.

1. **Chunking/Embedding**: Admin saves KB article → split into per-section chunks → OpenAI `text-embedding-3-small` converts to 1,536-dim vectors.
2. **Storing**: Vectors saved in ChromaDB (`storage/kb/chroma`).
3. **Searching**: User query → convert to vector → ChromaDB finds 5 closest chunks (cosine similarity).
4. Returns top chunks to `nodes.py → evaluate_context()` and `draft_resolution()`.

---

## 🔄 6. Ticket Reopen (`app/routers/tickets.py`)

Users can reopen wrongly-closed tickets via `POST /api/tickets/{id}/reopen`:

1. Validates ticket status is `resolved` or `closed`.
2. Sets status back to `open`.
3. Adds a system message: "Ticket reopened by user — problem not resolved."
4. Broadcasts via WebSocket so admin dashboard updates instantly.
5. Frontend re-enables the chat input and hides the feedback card.

---

## ⚙️ 7. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| OPENAI_API_KEY | — | Required |
| DATABASE_URL | sqlite+aiosqlite:///./storage/agent.db | SQLite path |
| LLM_MODEL | gpt-4.1-mini | Main drafting model |
| LLM_FAST_MODEL | gpt-4.1-nano | Fast triage/eval/classification model |
| LLM_TEMPERATURE | 0.1 | Creativity level (lower = more deterministic) |
| EVAL_THRESHOLD | 0.4 | Minimum context confidence before escalating |
| STT_MODEL | whisper-1 | Speech-to-text |
| EMBEDDING_MODEL | text-embedding-3-small | RAG embeddings |

---

## ⚙️ 8. Summary of Request Lifecycles

### When a User speaks to the Agent (Chat or Voice)
1. React `POST`'s to `/api/chat` OR `/api/voice/transcribe`.
2. `chat.py` runs the `agent_graph` (`graph.py`).
3. `triage()` classifies intent using fast model.
4. If `rag_needed`: `retrieval()` searches ChromaDB, `evaluate_context()` rates confidence, `draft_resolution()` writes reply.
5. If `resolve`: `handle_resolution()` auto-closes ticket (skips extra LLM call).
6. `ticket_action()` determines DB action (if not already set).
7. `chat.py` saves records and broadcasts via WebSocket.

### When an Admin talks to a User
1. React Admin clicks *Send* → `POST /api/tickets/{id}/reply`.
2. `tickets.py` saves message as `role="admin"` directly (no agent involved).
3. Broadcasts via WebSocket, user sees `🛡️ Administration` badge instantly.

### When a User Reopens a Resolved Ticket
1. User clicks *Reopen Ticket* → `POST /api/tickets/{id}/reopen`.
2. Backend validates status, sets to `open`, adds system message.
3. Broadcasts update, frontend re-enables chat, agent processes next message normally.
