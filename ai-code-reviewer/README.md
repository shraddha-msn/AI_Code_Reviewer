# AI Code Reviewer

A full-stack web app that fetches a public GitHub repository, runs it through Google Gemini, and returns a structured code review with bugs, quality issues, and concrete fixes.

**Stack**
- Backend: FastAPI · SQLAlchemy (SQLite) · `google-genai` SDK
- Frontend: React · Vite · Tailwind CSS · React Router · Axios

---

## Project layout

```
ai-code-reviewer/
├── backend/
│   ├── main.py        # FastAPI endpoints
│   ├── github.py      # GitHub repo fetcher
│   ├── llm.py         # Gemini integration
│   ├── models.py      # SQLAlchemy models
│   ├── schemas.py     # Pydantic schemas
│   ├── database.py    # DB engine + session
│   ├── requirements.txt
│   └── .env           # GEMINI_API_KEY, GITHUB_TOKEN (not committed)
└── frontend/
    ├── src/
    │   ├── pages/     # Home, Results, History
    │   ├── components/# ReviewCard, SeverityBadge
    │   ├── api.js
    │   ├── App.jsx
    │   └── main.jsx
    ├── index.html
    └── package.json
```

---

## Backend setup

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env` (copy from `.env.example`):

```
GEMINI_API_KEY=your-gemini-key
GITHUB_TOKEN=optional-pat-for-higher-rate-limits
GEMINI_MODEL=gemini-2.0-flash
```

Get a free Gemini key at https://aistudio.google.com/apikey.

Run the API:

```powershell
uvicorn main:app --reload --port 8000
```

Interactive docs: http://localhost:8000/docs

### Endpoints

| Method | Path                  | Description                       |
| ------ | --------------------- | --------------------------------- |
| POST   | `/api/review`         | Body: `{ "repo_url": "..." }`     |
| GET    | `/api/reviews`        | Last 50 reviews                   |
| GET    | `/api/reviews/{id}`   | One review by id                  |
| GET    | `/api/health`         | Health check                      |

---

## Frontend setup

```powershell
cd frontend
npm install
npm run dev
```

Vite serves the app at http://localhost:5173 and proxies `/api/*` to the FastAPI backend on port 8000.

---

## How it works

1. User pastes a GitHub URL on the Home page.
2. Backend parses `owner/repo`, lists the default branch's git tree, and downloads source files (skips `node_modules`, `dist`, etc.). Caps: 30 files, 50 KB per file, 200 KB total.
3. Files are concatenated into a prompt and sent to Gemini with `response_mime_type="application/json"`.
4. The structured response (score, summary, bugs, quality_issues, suggestions) is persisted to SQLite and returned.
5. Results page renders tabs with severity-tagged cards and before/after diffs for suggestions.

---

## Deployment notes

- **Backend**: Render.com free tier — point at `backend/`, build with `pip install -r requirements.txt`, start with `uvicorn main:app --host 0.0.0.0 --port $PORT`. Set env vars in the dashboard.
- **Frontend**: Vercel — point at `frontend/`. Update `vite.config.js` proxy or set the API base URL via env to your deployed backend.

---

## Future improvements

- Streaming responses (SSE) for token-by-token review output
- File-tree picker to review specific files
- Public share links per review
- GitHub OAuth for private repos
