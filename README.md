# Financial Document Analyzer

AI-powered financial PDF analysis using CrewAI, FastAPI, Celery, Redis, and MongoDB.

---

## Bugs Fixed

| # | File | Bug | Fix |
|---|------|-----|-----|
| 1 | `main.py` | `run_crew()` called directly in request — blocked server for minutes | Moved to Celery background task, returns `job_id` instantly |
| 2 | `main.py` | File deleted before Celery worker could read it | Moved cleanup to worker's `finally` block |
| 3 | `main.py` | No queue — concurrent uploads caused failures | Added Redis + Celery queue worker model |
| 4 | `tasks_queue.py` | Agents imported at module level, broke in worker process | Imports moved inside task function |
| 5 | — | Results lost after Redis 1hr TTL | Added MongoDB to persist results permanently |
| 6 | — | No user system | Added JWT auth + user accounts + analysis history |

---

## Setup

**Requirements:** Python 3.10+, Memurai (Redis), MongoDB

```bash
pip install -r requirements.txt
```

Add to `.env`:
```
GROQ_API_KEY=your_key
REDIS_URL=redis://localhost:6379/0
MONGO_URL=mongodb://localhost:27017
MONGO_DB_NAME=financial_analyzer
JWT_SECRET=your-secret
```

---

## Running

**Terminal 1 — API:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Worker:**
```bash
celery -A celery_worker.celery_app worker --loglevel=info --concurrency=2 --pool=solo
```

Open `http://localhost:8000` · Swagger at `http://localhost:8000/docs`

---

## API

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | — | Register new account |
| `POST` | `/auth/login` | — | Login, returns JWT token |
| `GET` | `/auth/me` | ✓ | Current user info |
| `POST` | `/analyze` | Optional | Upload PDF, returns `job_id` |
| `GET` | `/status/{job_id}` | — | Poll for result |
| `GET` | `/history` | ✓ | Last 20 analyses |

### `/analyze` request
```
multipart/form-data
  file   — PDF file (required)
  query  — Analysis question (optional)
```

### `/analyze` response
```json
{ "job_id": "abc-123", "status": "QUEUED" }
```

### `/status/{job_id}` response
```json
{ "status": "SUCCESS", "result": { "analysis": "..." } }
```

Status values: `PENDING` → `STARTED` → `SUCCESS` / `FAILURE`

---

## Project Structure

```
├── main.py           # API endpoints + auth
├── celery_worker.py  # Celery + Redis config
├── tasks_queue.py    # Background task (runs CrewAI)
├── database.py       # MongoDB helpers
├── agents.py         # CrewAI agents
├── task.py           # CrewAI tasks
├── tools.py          # PDF reader + analysis tools
├── index.html        # Web UI
└── .env              # Environment variables
```