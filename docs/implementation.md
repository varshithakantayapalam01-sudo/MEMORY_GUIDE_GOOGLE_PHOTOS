# Memory Guide — Technical Implementation Plan

---

## 1. Technology Stack & Configuration

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | Next.js 14+ (App Router, TypeScript) | Vercel-native, RSC support, fast interactive rendering |
| **Frontend Styling** | Vanilla CSS (custom design tokens) | Premium bespoke aesthetics, no utility framework bloat |
| **Backend** | Python 3.11+ / FastAPI | Best AI SDK support (`google-genai`), Pydantic validation, async |
| **AI Models** | Configurable via `GEMINI_MODEL` and `EMBEDDING_MODEL` | Dynamic model selection from environment variables |
| **Analytics Persistence** | SQLite (`sqlite3`) on Railway Volume | Immediate outcome persistence; stores ONLY numeric metrics & text |
| **Export Protection** | Protected via `ANALYTICS_ADMIN_TOKEN` header | Restricts research data access to authorized researchers |
| **Temp Storage** | Session-isolated (`/tmp/research_sessions/`) | Auto-cleared temporary storage for Research Mode uploads |
| **Hosting** | Vercel (Frontend) + Railway (Backend) | Production deployment targets |

---

## 2. Environment Configuration (`backend/.env`)

```bash
# Configurable Gemini Models
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=text-embedding-004
GEMINI_API_KEY=AIzaSy...

# Admin Security Token for Analytics Export
ANALYTICS_ADMIN_TOKEN=sk_research_admin_8f92a11b

# Server & Persistence Config
PORT=8000
HOST=0.0.0.0
DB_PATH=/data/memory_guide.db
TEMP_UPLOAD_DIR=/tmp/research_sessions

# CORS Config
FRONTEND_URL=https://memory-guide.vercel.app
ALLOWED_ORIGINS=http://localhost:3000,https://memory-guide.vercel.app
```

---

## 3. Data Schemas & Models

### 3.1 RetrievalSession Schema (`models/session.py`)

```python
from pydantic import BaseModel, Field

class Clue(BaseModel):
    dimension: str
    value: str
    source: str          # "user_initial", "user_answer", "inferred"
    certainty: str       # "definite", "probable", "unsure", "inferred"

class RetrievalSession(BaseModel):
    session_id: str
    mode: str            # "demo" or "research"
    original_query: str = ""
    clues: list[Clue] = []
    
    # Coverage Tracking
    dimensions_asked: set[str] = Field(default_factory=set)
    subattributes_asked: set[str] = Field(default_factory=set)
    dimensions_provided_by_user: set[str] = Field(default_factory=set)
    consecutive_idk_count: int = 0
    
    # Candidate Pools
    active_candidates: list[dict] = []
    reserve_candidates: list[dict] = []
    explicitly_rejected_ids: set[str] = Field(default_factory=set)
    
    # Lifecycle & Analytics
    round_count: int = 0
    retrieval_status: str = "created"  # "created", "in_progress", "found", "unresolved", "abandoned"
    start_time: float
    end_time: float | None = None
    final_target_id: str | None = None
```

---

## 4. API Endpoint Contracts & Security

### 4.1 Immediate Terminal Outcome Persistence & Feedback API

#### Terminal Selection (`POST /sessions/{sessionId}/select`)
When a user selects `"found"` or fallback reaches `"unresolved"` / `"abandoned"`:
1. `session.retrieval_status` is updated.
2. `analytics_db.save_completed_session(session)` is called **immediately** to insert core session data into SQLite.
3. Response is returned to UI.

#### End-of-Session Survey (`POST /sessions/{sessionId}/feedback`)
**Request**:
```json
{
  "helpfulnessRating": 5,
  "qualitativeFeedback": "The question about the birthday cake narrowed it down immediately."
}
```

**Handler Execution**:
Calls `analytics_db.update_session_feedback(sessionId, helpfulnessRating, qualitativeFeedback)` to update the existing SQLite record.

---

### 4.2 Protected Analytics Export (`GET /api/v1/analytics/export`)

**Header Required**:
`X-Admin-Token: <ANALYTICS_ADMIN_TOKEN>`

**FastAPI Route Implementation**:

```python
from fastapi import APIRouter, Header, HTTPException, status
from app.config import settings
from app.services import analytics_db

router = APIRouter()

@router.get("/analytics/export")
async def export_analytics(x_admin_token: str = Header(None)):
    if not settings.ANALYTICS_ADMIN_TOKEN or x_admin_token != settings.ANALYTICS_ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing analytics admin token."
        )
    
    data = analytics_db.get_all_completed_sessions()
    return {"success": True, "data": data}
```

---

## 5. Core Discrimination & Coverage Logic

### 5.1 Subattribute Split Score Calculation (`services/discrimination.py`)

```python
def select_next_best_question(session: RetrievalSession) -> QuestionSelection | None:
    """
    Selects the single best candidate-aware dimension or subattribute to ask about.
    Calculates subattribute split scores for list dimensions using: split_score = 1 - |2p - 1|
    """
    active = session.active_candidates
    if not active:
        return None

    total_score = sum(c["score"] for c in active)
    if total_score == 0:
        return None

    candidates_for_eval = []

    # Evaluate Subattributes for List Dimensions (objects, clothing, colors)
    list_dimensions = ["objects", "clothing", "dominant_colors"]
    for dim in list_dimensions:
        # Collect distinct subattributes across active candidates
        sub_values = set()
        for c in active:
            vals = c["profile"].get(dim, [])
            if isinstance(vals, list):
                sub_values.update(vals)

        for val in sub_values:
            sub_key = f"{dim}:{val}"
            
            # Exclusion Check
            if dim in session.dimensions_asked or sub_key in session.subattributes_asked or dim in session.dimensions_provided_by_user:
                continue

            # Calculate relevance-weighted presence probability p
            p = sum(c["score"] for c in active if val in c["profile"].get(dim, [])) / total_score
            
            # Split Score
            split_score = 1.0 - abs(2.0 * p - 1.0)
            m_weight = MEMORABILITY_WEIGHTS.get(dim, 0.7)
            final_score = split_score * m_weight

            candidates_for_eval.append({
                "type": "subattribute",
                "dimension": dim,
                "subattribute_key": sub_key,
                "value": val,
                "final_score": final_score
            })

    # Evaluate Categorical Dimensions (setting, occasion, people_count, etc.)
    cat_dimensions = ["setting", "occasion", "people_count", "time_of_day", "setting_type", "activity"]
    for dim in cat_dimensions:
        if dim in session.dimensions_asked or dim in session.dimensions_provided_by_user:
            continue

        weighted_dist = {}
        for c in active:
            val = c["profile"].get(dim, "unclear")
            if val != "unclear":
                weighted_dist[val] = weighted_dist.get(val, 0.0) + (c["score"] / total_score)

        if not weighted_dist:
            continue

        max_p = max(weighted_dist.values())
        split_score = 1.0 - max_p
        m_weight = MEMORABILITY_WEIGHTS.get(dim, 0.8)
        final_score = split_score * m_weight

        candidates_for_eval.append({
            "type": "categorical",
            "dimension": dim,
            "final_score": final_score
        })

    if not candidates_for_eval:
        return None

    candidates_for_eval.sort(key=lambda x: x["final_score"], reverse=True)
    best = candidates_for_eval[0]

    if best["final_score"] < MIN_QUESTION_VALUE:
        return None

    return best
```

---

### 5.2 Strict "I Don't Remember" Handling (`routes/sessions.py`)

```python
@router.post("/sessions/{sessionId}/answer")
async def process_answer(sessionId: str, payload: AnswerPayload):
    session = session_manager.get_session(sessionId)
    
    # Check if answer indicates uncertainty ("I don't remember")
    if is_idk_answer(payload.answer):
        # 1. Mark tested item as asked
        if payload.subattribute_key:
            session.subattributes_asked.add(payload.subattribute_key)
        else:
            session.dimensions_asked.add(payload.dimensionTested)

        # 2. ZERO score penalties or rescoring applied
        # 3. Increment consecutive_idk_count
        session.consecutive_idk_count += 1

        # 4. Check if 3 consecutive IDKs reached -> Trigger early candidate display
        if session.consecutive_idk_count >= 3:
            return {
                "success": True,
                "data": {
                    "action": "show_candidates",
                    "candidates": session.active_candidates[:6],
                    "message": "Let's take a look at the best matches so far."
                }
            }

        # 5. Immediately choose next best question
        next_q = select_next_best_question(session)
        return format_question_response(session, next_q)

    # Valid answer processing
    session.consecutive_idk_count = 0  # reset IDK counter
    clue = parse_clue_with_certainty(payload.answer, payload.dimensionTested)
    session.clues.append(clue)
    rescore_and_update_pools(session)
    ...
```

---

## 6. SQLite Analytics Persistence Interface (`services/analytics_db.py`)

```python
import sqlite3
import json
from app.config import settings

def init_db():
    with sqlite3.connect(settings.DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS research_sessions (
                session_id TEXT PRIMARY KEY,
                started_at TEXT,
                ended_at TEXT,
                library_mode TEXT,
                retrieval_status TEXT,
                original_description TEXT,
                total_time_seconds INTEGER,
                questions_to_target INTEGER,
                idk_count INTEGER,
                final_target_id TEXT,
                candidate_reduction_json TEXT,
                clues_json TEXT,
                question_helpfulness_rating INTEGER,
                qualitative_feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_completed_session(session):
    """
    IMMEDIATELY persists core session outcome when terminal state is reached.
    Does NOT store raw image files or photo bytes.
    """
    with sqlite3.connect(settings.DB_PATH) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO research_sessions (
                session_id, started_at, ended_at, library_mode, retrieval_status,
                original_description, total_time_seconds, questions_to_target,
                idk_count, final_target_id, candidate_reduction_json, clues_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.session_id,
            session.start_time,
            session.end_time,
            session.mode,
            session.retrieval_status,
            session.original_query,
            int(session.end_time - session.start_time),
            session.round_count,
            session.consecutive_idk_count,
            session.final_target_id,
            json.dumps(session.candidate_history),
            json.dumps([c.dict() for c in session.clues])
        ))
        conn.commit()

def update_session_feedback(session_id: str, rating: int, feedback: str):
    """
    Updates optional end-of-session survey results on existing SQLite row.
    """
    with sqlite3.connect(settings.DB_PATH) as conn:
        conn.execute("""
            UPDATE research_sessions
            SET question_helpfulness_rating = ?, qualitative_feedback = ?
            WHERE session_id = ?
        """, (rating, feedback, session_id))
        conn.commit()
    return True
```

---

## 7. Research Protocol Note

> **HYPOTHESIS VALIDATION PROTOCOL**:
> In Research Mode, study participants MUST NOT visually browse or select their target photo immediately prior to performing the retrieval task.
> Facilitators must preload the candidate photo batch beforehand or accept an unbrowsed folder input before task initiation.

---

*This document completes the pre-implementation specifications for Memory Guide MVP.*
