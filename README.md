# Support Desk AI Agent

AI-powered support agent that handles IT, DevOps, Sales, Network, and Security requests via chat or voice. Creates tickets automatically and routes them to the right team.

## Quick Start

### Backend

```bash
cd api
python -m venv .venv
.venv\Scripts\activate        # Windows or . .venv/Scripts/activate
pip install -r requirements.txt
pip install chromadb

# Set your OpenAI key
cp .env.example .env
# Edit .env → OPENAI_API_KEY=sk-...

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd front
npm install
npm install react-router-dom date-fns clsx
npm run dev
```

Open **http://localhost:5173**

## Pages

| Page | URL | Description |
|------|-----|-------------|
| **Chat** | `/` | User talks to AI agent. Agent answers and creates tickets. |
| **Tickets** | `/admin` | Admin views all tickets, conversations, and agent reasoning. |
| **KB** | `/kb` | Admin manages knowledge base articles (vector search). |

## How It Works

```
User sends message (chat or voice)
  → Agent searches Knowledge Base (RAG / vector search)
  → Agent generates reply + decides ticket (team, priority)
  → Ticket created in DB with conversation + reasoning steps
  → Admin sees everything in /admin
```

## Teams

| Team | Handles |
|------|---------|
| Help Desk | Laptop, password, software issues |
| DevOps | Server, database, deployment issues |
| Sales | Pricing, licensing, contracts |
| Network | VPN, WiFi, firewall, printer |
| Security | Phishing, access requests, certificates |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message → get agent reply + ticket |
| POST | `/api/voice/transcribe` | Upload audio → STT → agent reply + ticket |
| GET | `/api/tickets` | List tickets (filter by team/status) |
| GET | `/api/tickets/:id` | Ticket detail with messages + agent steps |
| PATCH | `/api/tickets/:id` | Update ticket status/assignment |
| GET | `/api/kb/search?q=...` | Semantic vector search |
| GET/POST/PUT/DELETE | `/api/kb/documents` | KB document CRUD |

## Tech Stack

- **Backend**: Python, FastAPI, LangGraph, OpenAI (GPT-4o, Whisper, text-embedding-3-small), ChromaDB, SQLite
- **Frontend**: React 19, TypeScript, Vite, TanStack Query, Zustand
- **RAG**: ChromaDB vector store, section-level chunking, cosine similarity search