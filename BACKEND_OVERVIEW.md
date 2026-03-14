# Backend Overview

## Architecture

```
User (chat/voice)
  → FastAPI Router (/api/chat or /api/voice/transcribe)
    → LangGraph Agent (2 nodes)
      → Node 1: understand — search KB via RAG
      → Node 2: respond — LLM generates reply + ticket decision
    → Ticket Service — saves ticket, messages, agent steps to SQLite
  → JSON response {reply, ticket}
```

## File Structure

```
api/
├── app/
│   ├── main.py                  # FastAPI app, 4 routers, lifespan
│   ├── core/
│   │   ├── config.py            # Pydantic Settings (env vars)
│   │   └── event_bus.py         # In-memory pub/sub (for WS)
│   ├── db/
│   │   ├── engine.py            # SQLAlchemy async engine + session
│   │   └── models.py            # Ticket, Message, AgentStep
│   ├── services/
│   │   ├── ticket_service.py    # CRUD: tickets, messages, agent steps
│   │   ├── rag_service.py       # ChromaDB + OpenAI embeddings + chunking
│   │   └── audio_service.py     # Whisper STT transcription
│   ├── agent/
│   │   ├── state.py             # AgentState TypedDict
│   │   ├── prompts.py           # System prompt (teams, priorities, KB)
│   │   ├── nodes.py             # understand + respond nodes
│   │   └── graph.py             # LangGraph: understand → respond → END
│   ├── routers/
│   │   ├── chat.py              # POST /api/chat
│   │   ├── voice.py             # POST /api/voice/transcribe
│   │   ├── tickets.py           # GET/PATCH /api/tickets
│   │   └── kb.py                # KB search + CRUD
│   └── tools/                   # Investigation tools (used by agent)
│       ├── base.py, alerts.py, metrics.py, logs.py, command.py,
│       ├── topology.py, contacts.py, wiki.py, network.py,
│       ├── config_analysis.py, video.py, registry.py
├── storage/
│   ├── agent.db                 # SQLite database
│   ├── audio/                   # Uploaded voice recordings
│   └── kb/
│       ├── seed_data.json       # 7 runbook articles
│       └── chroma/              # ChromaDB vector index
└── .env                         # OPENAI_API_KEY, models config
```

## Agent Flow

### Node 1: `understand`
- Takes user message
- Searches KB via ChromaDB (semantic vector search)
- Records search step for admin visibility

### Node 2: `respond`
- Receives KB results + user message
- LLM (GPT-4o) with structured output generates:
  - `reply` — friendly text answer
  - `should_create_ticket` — bool
  - `team` — help_desk / devops / sales / network / security
  - `priority` — P1 / P2 / P3 / P4
  - `title` — ticket title
  - `summary` — internal summary
- Records decision step for admin visibility

## RAG System

- **Storage**: `seed_data.json` — 7 articles covering all 5 teams
- **Chunking**: Section-level. Each section = 1 chunk. Document title prepended for context.
- **Embedding**: OpenAI `text-embedding-3-small` ($0.00002/1K tokens)
- **Vector store**: ChromaDB with cosine similarity, persisted to `storage/kb/chroma/`
- **Auto-index**: First search triggers indexing. CRUD mutations rebuild index.
- **Admin CRUD**: Full REST API at `/api/kb/documents`

## Database Models

### Ticket
`id, title, team, priority, status, created_by, assigned_to, summary, created_at, updated_at`

### Message
`id, ticket_id, role (user/agent/system), content, channel (chat/voice/email), metadata_json, created_at`

### AgentStep
`id, ticket_id, step_type (kb_search/decision/tool_call), tool_name, input_data, output_data, created_at`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| OPENAI_API_KEY | — | Required |
| DATABASE_URL | sqlite+aiosqlite:///./storage/agent.db | SQLite path |
| LLM_MODEL | gpt-4.1-mini | Main drafting model |
| LLM_FAST_MODEL | gpt-4.1-nano | Fast triage/eval/classification |
| LLM_TEMPERATURE | 0.1 | Creativity level |
| EVAL_THRESHOLD | 0.4 | Min context confidence before escalating |
| STT_MODEL | whisper-1 | Speech-to-text |
| EMBEDDING_MODEL | text-embedding-3-small | RAG embeddings |

