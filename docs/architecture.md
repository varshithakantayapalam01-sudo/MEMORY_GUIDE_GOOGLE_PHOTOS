# Memory Guide — Reasoning Architecture

---

## Overview

This document specifies the reasoning architecture for Memory Guide's core retrieval loop. It answers: **given what the user has already told me and the candidate photos remaining, what is the single most useful thing I should ask them next?**

The architecture is split into four core layers:

1. **Library & Privacy Layer** — manages Demo Mode and Research/Test Mode library contexts and temporary file lifecycles.
2. **Data Layer** — represents images, candidate pools, and structured user/inferred clues with certainty levels and coverage tracking.
3. **Reasoning Layer** — candidate scoring, subattribute-level discrimination analysis, clue certainty weighting, and question selection.
4. **Session & Persistence Layer** — session state transitions, immediate SQLite outcome logging, and protected analytics export.

---

## The Retrieval Loop

```
Select Mode: Demo (Seeded) OR Research (Upload/Preload - unbrowsed by participant)
  │
  ▼
User vague description
  │
  ▼
┌─────────────────────────────┐
│  1. QUERY UNDERSTANDING     │  LLM parses free-form text → structured clues
│     & COVERAGE INITIALIZATION│  Populate dimensions_provided_by_user
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  2. INITIAL RETRIEVAL &     │  Score library images against clues
│     POOL PARTITIONING       │  Partition: active_candidates | reserve_candidates
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  3. SUBATTRIBUTE DISCRIMINATION│ For list dimensions: split_score = 1 - |2p - 1|
│     ANALYSIS                │  Exclude items in dimensions_asked/subattributes_asked
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  4. QUESTION SELECTION      │  Select highest split_score × memorability_weight
│                             │  (e.g., "objects:cake")
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  5. ASK USER                │  LLM phrases natural question for selected item
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  6. INTERPRET ANSWER        │  Check for "I Don't Remember" vs valid clue
└──────────────┬──────────────┘
               │
               ├─ User answered "I Don't Remember":
               │  - Add dimension/subattribute to asked tracking
               │  - Apply ZERO score penalty or rescore
               │  - Increment consecutive_idk_count
               │  - Loop back to Step 3 (or Step 8 if consecutive_idk_count >= 3)
               │
               ▼
┌─────────────────────────────┐
│  7. SAFE CANDIDATE RESCORE  │  Rescore using certainty weights (definite > probable > inferred)
│     & POOL MANAGEMENT       │  Move low scores to reserve; user rejections to rejected.
│                             │  NO negative attribute transfer!
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  8. TERMINATION CHECK       │
│                             │
│  active ≤ 6 OR idk ≥ 3? ───┼──→  SHOW FOR RECOGNITION
│  active == 0?     ──────────┼──→  RECOVER FROM RESERVE POOL
│  rounds ≥ 5?      ──────────┼──→  FALLBACK / UNRESOLVED
│  otherwise        ──────────┼──→  LOOP BACK TO STEP 3
└─────────────────────────────┘
               │
               ▼
┌─────────────────────────────┐
│  9. RECOGNITION & "CLOSE"   │  User selects: "This is it" / "This looks close" / "None"
│                             │  "Close" → visual reference comparison → ask next question
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ 10. IMMEDIATE SQLITE PERSIST│  Save session outcome IMMEDIATELY upon terminal state
│     & OPTIONAL SURVEY       │  Feedback endpoint UPDATES existing SQLite record
└─────────────────────────────┘
```

---

## 1. Library Modes & Research Protocol

### 1.1 Operating Modes
- **Demo Mode**: Seeded synthetic library (~55 photos) for public showcase.
- **Research / Test Mode**: Allows upload of a limited personal photo set or facilitator preloading of a participant-specific test library.

### 1.2 Research Protocol Constraint (Hypothesis Validation)
- **Constraint**: Participants must NOT manually browse or curate the candidate photo set immediately before initiating retrieval. Visual exposure to the candidate set prior to retrieval invalidates vague-memory research.
- **Protocol**: Photos must be preloaded by a facilitator OR provided via a bulk unbrowsed upload before the task begins.

### 1.3 Privacy & Data Retention
- Temporary files stored in `/tmp/research_sessions/{session_id}/` are automatically deleted upon session termination or timeout.
- Persistent SQLite analytics (`/data/memory_guide.db`) **never store raw image files or photo bytes** — only structured numeric metrics and anonymized session logs.

---

## 2. Coverage Tracking & "I Don't Remember" Architecture

### 2.1 Coverage Tracking Schema
Each `RetrievalSession` maintains explicit sets to prevent duplicate questions:

```json
{
  "dimensions_asked": ["setting", "time_of_day"],
  "subattributes_asked": ["objects:cake", "clothing:pink_dress"],
  "dimensions_provided_by_user": ["activity", "people_count"],
  "consecutive_idk_count": 0
}
```

### 2.2 Exclusion Rules
Before evaluating candidate attributes, the system excludes any dimension or subattribute present in:
- `dimensions_asked`
- `subattributes_asked`
- `dimensions_provided_by_user`

*Example*: If the user stated *"I was wearing a pink dress"*, `clothing` and `clothing:pink_dress` are marked as provided, preventing questions like *"What color were your clothes?"*. If `objects:cake` was asked, it cannot be re-asked, but `objects:balloons` remains eligible if it offers high discrimination.

### 2.3 Strict "I Don't Remember" Handling
When a user responds with uncertainty (*"I don't remember"*, *"not sure"*, *"can't recall"*):
1. Add the tested dimension or subattribute to `dimensions_asked` / `subattributes_asked`.
2. Add **NO** new clue to the active clue set.
3. Apply **ZERO** penalty to any candidate image.
4. Do **NOT** rescore or re-rank candidate pools.
5. Increment `consecutive_idk_count` by 1.
6. Immediately select the next best candidate-aware question.
7. If `consecutive_idk_count >= 3`: Stop asking questions and display the current top active candidates for recognition immediately.

---

## 3. Subattribute-Level Discrimination for Multi-Value Attributes

### 3.1 Categorical vs. List Dimensions
- **Categorical Dimensions** (`setting`, `occasion`, `people_count`, `time_of_day`): Evaluated using relevance-weighted categorical value distributions ($1 - \text{weighted\_max\_fraction}$).
- **List Dimensions** (`objects`, `clothing`, `dominant_colors`): Evaluated strictly at the **subattribute level**.

### 3.2 Relevance-Weighted Presence Probability
For a list subattribute $v$ (e.g., `objects:cake`, `clothing:pink_dress`):
Compute presence probability $p(v)$ across active candidates $c_i$ with normalized relevance weights $w_i$:
$$p(v) = \sum_{i: v \in c_i.\text{attributes}} w_i$$

### 3.3 Subattribute Split Score
Calculate the discrimination split score:
$$\text{split\_score}(v) = 1.0 - |2 \cdot p(v) - 1.0|$$

- $p(v) = 0.50 \implies \text{split\_score} = 1.0$ (Perfect 50/50 split across candidate relevance)
- $p(v) = 0.10 \text{ or } 0.90 \implies \text{split\_score} = 0.20$ (Poor split)

### 3.4 Final Subattribute Question Score
$$\text{final\_score}(v) = \text{split\_score}(v) \times \text{memorability\_weight}(\text{dimension})$$

This produces specific, targeted questions (e.g., *"Was there a cake visible?"*, *"Do you remember wearing something pink?"*) rather than vague dimension questions.

---

## 4. Candidate Pool Management & Safe Rejection

### 4.1 Pool Definitions
- `active_candidates`: High-relevance candidates driving question selection.
- `reserve_candidates`: Lower-relevance candidates preserved for recovery.
- `explicitly_rejected_candidates`: Image IDs explicitly rejected by the user.

### 4.2 Removal of Negative Attribute Transfer
Rejecting a set of photos ("None of these") permanently moves those specific image IDs to `explicitly_rejected_candidates`. Shared attributes of rejected photos are **never** penalized on remaining candidates.

---

## 5. Immediate Outcome Persistence & Protected Analytics Export

```
Session reaches terminal state (found / unresolved / abandoned)
  │
  ▼
1. IMMEDIATELY INSERT record into SQLite (research_sessions)
   - session_id, status, description, time, question count, history, final target
  │
  ▼
2. Return terminal UI view + Optional End-of-Session Research Survey
  │
  ▼
3. User submits feedback (POST /sessions/{id}/feedback)
   - UPDATE existing SQLite record with helpfulness_rating & qualitative_feedback
```

### 5.1 SQLite Security & Privacy Constraint
- SQLite stores **only** structured session metrics and text responses.
- SQLite **never stores raw photo files, bytes, or personal images**.

### 5.2 Analytics Export Endpoint Security
- `GET /api/v1/analytics/export` requires the HTTP header:
  `X-Admin-Token: <ANALYTICS_ADMIN_TOKEN>`
- Unauthorized requests return HTTP 401.
- Public frontend users do not require or possess this token.

---

## 6. Configurable Model Environment Architecture

Gemini API calls dynamically load model names from `app/config.py`:
- `GEMINI_MODEL` (e.g., `gemini-2.5-flash`)
- `EMBEDDING_MODEL` (e.g., `text-embedding-004`)

---

## Summary Checklist

- [x] Full coverage tracking (`dimensions_asked`, `subattributes_asked`, `dimensions_provided_by_user`, `consecutive_idk_count`).
- [x] Subattribute split score $1 - |2p - 1|$ for list dimensions (`objects:cake`, etc.).
- [x] Immediate SQLite outcome persistence on terminal state; feedback endpoint updates record.
- [x] Analytics export protected by `ANALYTICS_ADMIN_TOKEN`; no photo bytes stored in SQLite.
- [x] Research protocol note included (unbrowsed participant preloading).
