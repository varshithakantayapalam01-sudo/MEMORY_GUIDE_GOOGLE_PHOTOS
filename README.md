# Memory Guide — MVP

> AI-guided vague-memory photo retrieval web application.

---

## Project Structure

```text
MEMORY_GUIDE_MVP/
├── docs/                      # PRD, Reasoning Architecture & Technical Plan
│   ├── requirements.md
│   ├── architecture.md
│   └── implementation.md
├── backend/                   # Python FastAPI service (Railway target)
│   ├── app/
│   │   ├── config.py          # Environment settings (Pydantic)
│   │   ├── main.py            # FastAPI entry point & CORS configuration
│   │   ├── models/            # Pydantic data schemas
│   │   ├── routes/            # API endpoints (/api/v1/health)
│   │   └── services/          # Database & business logic (analytics_db.py)
│   ├── tests/                 # Pytest suite
│   ├── requirements.txt
│   ├── Procfile               # Railway deployment configuration
│   ├── railway.toml
│   └── .env.example
├── frontend/                  # Next.js App Router frontend (Vercel target)
│   ├── src/
│   │   ├── app/               # Next.js App Router (layout.tsx, page.tsx, globals.css)
│   │   └── lib/               # API wrapper (api.ts)
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   └── .env.example
├── .gitignore
└── README.md
```

---

## Quick Start / Local Setup

### 1. Backend Setup (FastAPI)

Requires **Python 3.11+**.

```bash
cd backend

# Create & activate virtual environment (Python 3.11+)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run development server
uvicorn app.main:app --reload --port 8000
```

- **Backend Base URL**: `http://localhost:8000`
- **Health Endpoint**: `http://localhost:8000/api/v1/health`
- **Swagger Documentation**: `http://localhost:8000/docs`

#### Running Backend Tests

```bash
cd backend
pytest
```

---

### 2. Frontend Setup (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Run development server
npm run dev
```

- **Frontend Application**: `http://localhost:3000`

---

## Phase 1 Verification Summary

- **Backend Health Check**: `GET http://localhost:8000/api/v1/health` returns `{"status":"ok","service":"memory-guide-api","version":"0.1.0"}`.
- **SQLite Database**: Automatically initializes `research_sessions` table at startup (`./data/memory_guide.db`).
- **Temp Storage**: Automatically creates temporary upload directory (`./tmp/research_sessions`).
- **Frontend Status**: `http://localhost:3000` displays Memory Guide landing UI and confirms live backend connection.
