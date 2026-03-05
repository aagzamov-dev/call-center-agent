# 🎙️ Incident AI Agent (Demo)

A production-shaped AI system for automated incident investigation and response. Built with **FastAPI**, **LangGraph**, and **React**.

## 🚀 Quick Start (Backend)

1. **Enter directory and activate venv**:
   ```bash
   cd api
   source .venv/Scripts/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file in the `api/` folder:
   ```ini
   OPENAI_API_KEY=your_key_here
   DATABASE_URL=sqlite+aiosqlite:///./storage/agent.db
   LLM_MODEL=gpt-4o
   TTS_MODEL=gpt-4o-mini-tts
   ```

4. **Run Server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **WebSocket**: `ws://localhost:8000/ws`

---

## 🤖 How the Agent Works

This system uses a **LangGraph StateGraph** to manage the agent's reasoning. Instead of a single "guess", the agent follows a multi-step investigation loop:

1. **Context Gathering**: Pulls topology, runbooks, and recent timeline events.
2. **Investigation Loop**: The AI calls tools (check metrics, search logs, run diagnostic commands) and reasons about the output.
3. **Structured Planning**: Once evidence is found, the AI produces a JSON plan with hypotheses and required actions.
4. **Automated Action**: Actions are validated by a `policy.py` layer. Safe actions (Chat/Ticket) execute automatically; risky ones (Voice Call) await your approval.

---

## 📚 Documentation
For a deep dive into the code structure and agent logic, see:
👉 [**BACKEND_OVERVIEW.md**](./BACKEND_OVERVIEW.md)