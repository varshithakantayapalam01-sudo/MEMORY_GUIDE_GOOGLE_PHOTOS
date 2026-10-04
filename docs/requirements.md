# Memory Guide — MVP Product Requirements Document

---

## 1. Target User

Users attempting to retrieve **one specific older personal photo** from a library of hundreds or thousands of images, where:

- They believe the photo exists.
- They can partially describe or recognize it.
- They cannot locate it using precise metadata (exact date, location, album name).
- Their initial search attempt returns broad, ambiguous, or unsuccessful results.

**MVP Personas**:
1. **Public Evaluators / Demo Users**: Showcase visitors exploring the system using a seeded synthetic photo library.
2. **Research Participants**: Study participants attempting vague-memory retrieval on a limited set of photos they genuinely remember (either self-uploaded or preloaded by a study facilitator).

---

## 2. User Problem

After an initial search returns too many partially relevant photos, the user is stuck deciding **"What should I try next?"** This leads to:

- Trial-and-error keyword changes.
- Guessing dates or scrolling through months/years.
- Switching to other apps (WhatsApp, social media) for clues.
- Asking other people for details.
- Giving up entirely.

The user often **does** remember enough information to identify the photo — the difficulty is not a memory deficit, but a *strategy* deficit: users don't know which of their remembered clues will actually help narrow the results.

---

## 3. Root Cause

The root cause is **not** that users cannot remember the photo. Users typically recall rich contextual details (people, clothing, setting, activity, occasion, emotional context).

The root cause is that **vague-memory retrieval requires progressively identifying which remembered clue will best discriminate the intended photo from other candidates** — and users lack the information to make that decision well. Specifically, users do not know:

1. Which of their remembered clues the system can understand and act on.
2. Which clue will meaningfully narrow the current candidate set.
3. What to try after an unsuccessful search attempt.
4. How to move from "many partially relevant photos" to "the one intended photo."

This turns retrieval into a user-led, trial-and-error process.

---

## 4. Product Hypothesis

> **"When an initial vague-memory photo search is ambiguous, AI-selected discriminative questions can help users identify the intended photo with fewer unguided reformulations and less manual scrolling."**

Instead of requiring the user to repeatedly invent new queries, the system:

1. Retrieves an initial candidate set from the user's vague description.
2. Inspects the remaining candidate photos.
3. Identifies which missing clue or subattribute would best reduce uncertainty across that set.
4. Asks the user **one** targeted clarification question.
5. Uses the answer to narrow candidates (managing active, reserve, and rejected pools).
6. Repeats only when necessary.
7. Presents a small candidate set for visual recognition.

---

## 5. Core User Journey

### Step 1 — Select Library Mode & Start Retrieval
The user chooses between:
- **Demo Mode**: Explore with a pre-seeded synthetic/demo dataset.
- **Research / Test Mode**: Upload a limited set of personal photos (or use a facilitator-preloaded private test library) for a genuine vague-memory retrieval task.

The system prompts with an open invitation:
> "What photo are you trying to find? Tell me anything you remember — you don't need to know the date or exact words."

### Step 2 — Understand Initial Memory & Assign Clue Certainty
The system extracts clues from the description and tracks provided dimensions (`dimensions_provided_by_user`). Clues receive certainty tags (`definite`, `probable`, `unsure`, or `inferred`).

### Step 3 — Generate Initial Candidate Set & Partition Pools
The system compares the description against available images and partitions candidates into `active_candidates`, `reserve_candidates`, and `explicitly_rejected_candidates`.

### Step 4 — Candidate-Aware Relevance-Weighted & Subattribute Analysis
The system performs relevance-weighted distribution analysis across current active candidates. For list-based attributes (objects, clothing, colors), it evaluates candidate-aware subattribute presence probabilities using $\text{split\_score} = 1 - |2p - 1|$.

### Step 5 — Ask ONE Adaptive Question & Track Coverage
The system selects the single highest-scoring eligible dimension or subattribute (excluding items in `dimensions_asked`, `subattributes_asked`, or `dimensions_provided_by_user`).

### Step 6 — Narrow Candidates Safely & Handle "I Don't Remember"
- On answer: update clues and re-score active/reserve pools. Explicit user rejection ("None of these") excludes *only* the specific photos shown without negative attribute transfer.
- On "I Don't Remember": add tested dimension/subattribute to `asked`, apply **zero penalty**, increment `consecutive_idk_count`, and immediately ask the next best question. If `consecutive_idk_count >= 3`, stop questioning early and present current top candidates.

### Step 7 — Recognition & "Close" Handling
When `active_candidates` is small (3–6 photos) or after 3 consecutive "I don't remember" responses, the system displays candidates for visual recognition:
- "Yes, this is it" → Triggers immediate SQLite session outcome save & displays optional research questions.
- "This looks close" → Uses selected image as a positive visual reference, compares it against remaining candidates, identifies key differences, and asks another candidate-aware question.
- "None of these" → Permanently excludes the shown images and continues search using remaining active/reserve pools.

### Step 8 — Optional End-of-Session Research Survey
After retrieval outcome is saved, the user can submit an optional 1–5 rating and feedback. The backend updates the existing SQLite record.

---

## 6. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-1 | Support two operational library modes: **Demo Mode** (seeded synthetic library) and **Research / Test Mode** (limited personal photo upload or facilitator preloaded library). |
| FR-2 | Implement privacy-preserving temporary/session-scoped storage for Research Mode uploads. Automatically delete raw uploaded photo files when session terminates. SQLite analytics must NEVER store raw photo bytes. |
| FR-3 | Accept free-form natural-language input describing a vaguely remembered photo. |
| FR-4 | Extract structured clues and assign explicit certainty levels (`definite`, `probable`, `unsure`, `inferred`). |
| FR-5 | Maintain candidate management pools (`active_candidates`, `reserve_candidates`, `explicitly_rejected_candidates`) with reserve recovery flow. |
| FR-6 | Formally track question coverage: `dimensions_asked`, `subattributes_asked`, `dimensions_provided_by_user`, and `consecutive_idk_count`. Exclude all previously covered dimensions/subattributes from future selection. |
| FR-7 | Formally support subattribute-level discrimination for list dimensions (`objects`, `clothing`, `dominant_colors`) using presence probability $p$ and $\text{split\_score} = 1 - |2p - 1|$. Select specific subattributes (e.g., `objects:cake`) rather than broad unspecific dimensions. |
| FR-8 | Handle "I Don't Remember" by adding dimension/subattribute to asked tracking, applying ZERO score penalty/rescoring, incrementing `consecutive_idk_count`, and immediately proceeding to the next best question. Show candidates early if `consecutive_idk_count >= 3`. |
| FR-9 | Weight clues by certainty (`definite > probable > unsure > inferred`). Ensure AI-inferred clues can never permanently eliminate a plausible target by themselves. |
| FR-10 | Support "This looks close" by using the selected candidate as a positive visual reference, analyzing remaining candidate differences relative to it, and selecting another candidate-aware discriminative question. |
| FR-11 | Display 3–6 candidate photos for visual recognition once the active candidate set is small or after 3 consecutive "I don't remember" responses. |
| FR-12 | Immediately persist core session outcomes (`found`, `unresolved`, `abandoned`) to SQLite upon reaching terminal state. Allow subsequent `POST /sessions/{id}/feedback` requests to update the record with optional research ratings and feedback. |
| FR-13 | Protect the research analytics export endpoint (`GET /api/v1/analytics/export`) using a secret environment token (`ANALYTICS_ADMIN_TOKEN`). Normal public frontend users do not require this token. |
| FR-14 | Restrict person-identity clues to generic visual attributes unless explicit identity metadata has been pre-tagged in the library. Do not perform automated face recognition. |
| FR-15 | Ensure AI model identifiers (`GEMINI_MODEL`, `EMBEDDING_MODEL`) are configurable via backend environment variables rather than hardcoded. |

---

## 7. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | The experience must feel calm, simple, visual, and intelligent — adhering to high-end design aesthetics (modern typography, dark/light harmonious themes, clean layout). |
| NFR-2 | Photos must remain visually dominant in the UI; the interface is not a chat window. |
| NFR-3 | Security & Privacy: Analytics storage must contain only structured session metadata; raw photo files/bytes must never be saved in SQLite. Export API must require `ANALYTICS_ADMIN_TOKEN`. |
| NFR-4 | Reliability: Completed research session outcomes must persist immediately to SQLite on a Railway volume to prevent data loss even if the feedback survey is skipped. |
| NFR-5 | Performance: Question generation round-trip latency must remain under 4 seconds. |
| NFR-6 | Model Flexibility: All AI model endpoints must dynamically resolve models from environment configuration. |
| NFR-7 | Clarification questions must not feel coercive; "I don't remember" must always be a zero-penalty option. |
| NFR-8 | The application must be deployed with frontend on Vercel and backend on Railway. |

---

## 8. MVP Scope

### In Scope
- Standalone web application with Next.js frontend (Vercel) and FastAPI backend (Railway).
- Dual library modes: Demo Mode (seeded dataset) and Research/Test Mode (small upload set / preloaded private library).
- Session-scoped image storage with explicit privacy cleanup for research mode.
- Clue extraction with certainty tagging (`definite`, `probable`, `unsure`, `inferred`).
- Candidate pool architecture (`active`, `reserve`, `explicitly_rejected`).
- Subattribute-level discrimination engine for list dimensions (`split_score = 1 - |2p - 1|`).
- Explicit coverage tracking (`dimensions_asked`, `subattributes_asked`, `dimensions_provided_by_user`, `consecutive_idk_count`).
- Immediate terminal state SQLite session persistence + optional survey update.
- Token-protected analytics export (`ANALYTICS_ADMIN_TOKEN`).
- Configurable model environment variables (`GEMINI_MODEL`, `EMBEDDING_MODEL`).

---

## 9. Explicit Non-Goals

The MVP **must not** build:
- A full Google Photos clone or sync client.
- Face recognition or automated person-name identification.
- Long-term permanent storage of participant personal photos in Research Mode.
- Storing raw personal image files or photo bytes in SQLite analytics.
- Unprotected public export endpoints for research data.
- Hard coded AI model strings.

---

## 10. Research Mode Testing Protocol Note

> **IMPORTANT PROTOCOL REQUIREMENT FOR HYPOTHESIS VALIDATION**:
> For research study sessions, participants MUST NOT manually browse or curate a small target-containing photo library immediately before performing the retrieval task. Seeing or selecting the target photo prior to the test invalidates vague-memory testing.
>
> **Preferred Setup**:
> - A study facilitator preloads a participant-specific image batch before the task, OR
> - A participant provides/uploads an unbrowsed folder/batch before the target retrieval scenario is selected.
>
> The participant must begin the retrieval task relying solely on their episodic memory, without prior visual inspection of the candidate library.

---

## 11. Success Criteria & Research Metrics

### Research Analytics Metrics (Persisted in SQLite)
| Metric | Definition |
|--------|------------|
| Session ID | Unique session identifier. |
| Retrieval Status | `found`, `unresolved`, `abandoned`. |
| Library Mode | `demo` or `research`. |
| Time to Target | Seconds from initial memory entry to target selection. |
| Questions to Target | Total clarification rounds required. |
| Candidate Reduction History | Count of active candidates before and after each question. |
| IDK Count | Total "I don't remember" responses recorded (`consecutive_idk_count`). |
| Helpful Clues | Clues contributing to successful narrowing. |
| Question Helpfulness Rating | 1–5 scale post-session participant rating (updated via feedback endpoint). |
| Qualitative Feedback | Optional user text response regarding confusing/unhelpful aspects (updated via feedback endpoint). |

---

*This PRD defines the complete requirements for Memory Guide MVP.*
