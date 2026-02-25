# Financial Document Analyzer

AI-powered financial PDF analysis using CrewAI, FastAPI, Celery, and Redis.

---

## Bugs Fixed

| # | File | Bug | Fix |
|---|------|-----|-----|
| 1 | `main.py` | `run_crew()` called directly in request handler — blocked server for minutes per request | Moved to Celery background task, returns `job_id` instantly |
| 2 | `main.py` | File deleted in API `finally` block before Celery worker could read it | Moved file cleanup into worker's `finally` block |
| 3 | `main.py` | No queue — concurrent uploads competed for resources, caused failures and timeouts | Added Redis + Celery queue worker model |
| 4 | `main.py` | `asyncio` imported but never used | Removed unused import |
| 5 | `main.py` | `run_crew()` imported CrewAI agents at API level — unnecessary in API process | Removed crew logic from `main.py`, lives only in `tasks_queue.py` |
| 6 | `main.py` | No error detail returned on 500 — browser showed "Internal Server Error" with no info | Added global exception handler returning full traceback in response |
| 7 | `main.py` | No CORS middleware — browser UI could not call the API | Added `CORSMiddleware` allowing all origins |
| 8 | `main.py` | `/` endpoint returned JSON health check instead of serving the UI | Changed to return `FileResponse("index.html")` |
| 9 | `main.py` | Redis not running caused cryptic 500 with no useful message | Exception handler now surfaces the actual `ConnectionRefusedError` |
| 10 | `tasks_queue.py` | Agents imported at module level — broke in Celery worker process due to serialisation | Moved imports inside the task function |
| 11 | `tasks_queue.py` | Task had no retry logic — any transient error permanently failed the job | Added `max_retries=2` with exponential backoff |
| 12 | `celery_worker.py` | `worker_prefetch_multiplier` not set — workers grabbed multiple jobs unfairly | Set to `1` for fair one-task-at-a-time dispatch |
| 13 | `celery_worker.py` | `task_acks_late` not set — worker crash lost the job permanently | Set to `True` so job requeues if worker crashes mid-task |
| 14 | `celery_worker.py` | Windows incompatibility — default Celery multiprocessing pool fails on Windows | Used `--pool=solo` flag when starting worker |
| 15 | `.env` | `REDIS_URL` missing from environment config | Added all required keys to `.env` |

---

## Setup

**Requirements:** Python 3.10+, Memurai (Redis)

```bash
pip install -r requirements.txt
```

Add to `.env`:
```
GROQ_API_KEY=your_key
REDIS_URL=redis://localhost:6379/0
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

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web UI |
| `POST` | `/analyze` | Upload PDF, returns `job_id` |
| `GET` | `/status/{job_id}` | Poll for result |

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
├── main.py           # API endpoints
├── celery_worker.py  # Celery + Redis config
├── tasks_queue.py    # Background task (runs CrewAI)
├── agents.py         # CrewAI agents
├── task.py           # CrewAI tasks
├── tools.py          # PDF reader + analysis tools
├── index.html        # Web UI
└── .env              # Environment variables
```