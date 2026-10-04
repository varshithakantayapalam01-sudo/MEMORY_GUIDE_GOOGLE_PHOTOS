from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict
from app.models.clue import Clue
from app.models.candidate import CandidateEntry
from app.models.question import QuestionSelection, ClarificationQuestion
from app.models.session import (
    RetrievalSession,
    SessionMode,
    QuestionAnswerRecord,
    CandidateHistoryEntry,
)


class SessionNotFoundError(Exception):
    """Raised when a session ID does not exist."""

    pass


class InvalidSessionModeError(Exception):
    """Raised when an invalid session mode is provided."""

    pass


# In-memory session store
_sessions: Dict[str, RetrievalSession] = {}


def create_session(mode: str, session_id: Optional[str] = None) -> RetrievalSession:
    """
    Creates a new RetrievalSession and stores it in memory.
    """
    if mode not in ("demo", "research"):
        raise InvalidSessionModeError(f"Invalid session mode '{mode}'. Must be 'demo' or 'research'.")

    sid = session_id or f"sess_{uuid.uuid4().hex[:12]}"
    session = RetrievalSession(
        session_id=sid,
        mode=mode,  # type: ignore
        retrieval_status="created",
        started_at=datetime.now(timezone.utc),
    )
    _sessions[sid] = session
    return session


def get_session(session_id: str) -> Optional[RetrievalSession]:
    """
    Retrieves a session by ID, or None if not found.
    """
    return _sessions.get(session_id)


def delete_session(session_id: str) -> bool:
    """
    Deletes a session from memory and triggers research file cleanup if applicable.
    """
    session = _sessions.get(session_id)
    if session:
        if session.mode == "research":
            from app.services import upload_service
            upload_service.cleanup_research_session_files(session_id)
        del _sessions[session_id]
        return True
    return False


def clear_all_sessions() -> None:
    """
    Clears all active sessions and performs cleanup (used for test isolation).
    """
    from app.services import upload_service
    for sid, session in list(_sessions.items()):
        if session.mode == "research":
            upload_service.cleanup_research_session_files(sid)
    _sessions.clear()


def mark_dimension_asked(session_id: str, dimension: str) -> RetrievalSession:
    session = get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session '{session_id}' not found.")
    session.dimensions_asked.add(dimension)
    return session


def mark_subattribute_asked(session_id: str, subattribute_key: str) -> RetrievalSession:
    session = get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session '{session_id}' not found.")
    session.subattributes_asked.add(subattribute_key)
    return session


def mark_dimension_provided_by_user(session_id: str, dimension: str) -> RetrievalSession:
    session = get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session '{session_id}' not found.")
    session.dimensions_provided_by_user.add(dimension)
    return session


def add_clue(session_id: str, clue: Clue) -> RetrievalSession:
    session = get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session '{session_id}' not found.")
    session.clues.append(clue)
    if clue.dimension:
        session.dimensions_provided_by_user.add(clue.dimension)
    return session


def record_idk(session_id: str) -> RetrievalSession:
    """
    Records an 'I don't remember' response:
    - Increments consecutive_idk_count (used for early recognition triggering)
    - Increments total_idk_count (lifetime count, NEVER resets)
    """
    session = get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session '{session_id}' not found.")
    session.consecutive_idk_count += 1
    session.total_idk_count += 1
    return session


def reset_consecutive_idk(session_id: str) -> RetrievalSession:
    """
    Resets consecutive_idk_count to 0 upon receiving a valid answer.
    IMPORTANT: total_idk_count is NEVER reset.
    """
    session = get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session '{session_id}' not found.")
    session.consecutive_idk_count = 0
    return session


def record_question_answer(session_id: str, record: QuestionAnswerRecord) -> RetrievalSession:
    session = get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session '{session_id}' not found.")
    session.question_history.append(record)
    session.round_count = record.round
    return session


def set_candidate_pools(
    session_id: str,
    active: List[CandidateEntry],
    reserve: List[CandidateEntry]
) -> RetrievalSession:
    """
    Sets active and reserve candidate pools.
    STATE SAFETY RULE: Filter out any candidates present in explicitly_rejected_ids.
    Explicitly rejected candidates must NEVER return to active or reserve pools.
    """
    session = get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session '{session_id}' not found.")

    rejected = session.explicitly_rejected_ids
    filtered_active = [c for c in active if c.image_id not in rejected]
    filtered_reserve = [c for c in reserve if c.image_id not in rejected]

    # Update pool attribute on entries
    for c in filtered_active:
        c.pool = "active"
    for c in filtered_reserve:
        c.pool = "reserve"

    session.active_candidates = filtered_active
    session.reserve_candidates = filtered_reserve
    return session


def reject_candidate_ids(session_id: str, image_ids: List[str]) -> RetrievalSession:
    """
    Permanently rejects specified image IDs:
    - Adds IDs to explicitly_rejected_ids
    - Removes them from active_candidates and reserve_candidates
    """
    session = get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session '{session_id}' not found.")

    for img_id in image_ids:
        session.explicitly_rejected_ids.add(img_id)

    rejected = session.explicitly_rejected_ids
    session.active_candidates = [c for c in session.active_candidates if c.image_id not in rejected]
    session.reserve_candidates = [c for c in session.reserve_candidates if c.image_id not in rejected]
    return session


def mark_found(session_id: str, final_target_id: str) -> RetrievalSession:
    session = get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session '{session_id}' not found.")
    session.retrieval_status = "found"
    session.final_target_id = final_target_id
    session.ended_at = datetime.now(timezone.utc)
    if session.mode == "research":
        from app.services import upload_service
        upload_service.cleanup_research_session_files(session_id)
    return session


def mark_unresolved(session_id: str) -> RetrievalSession:
    session = get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session '{session_id}' not found.")
    session.retrieval_status = "unresolved"
    session.ended_at = datetime.now(timezone.utc)
    if session.mode == "research":
        from app.services import upload_service
        upload_service.cleanup_research_session_files(session_id)
    return session


def mark_abandoned(session_id: str) -> RetrievalSession:
    session = get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session '{session_id}' not found.")
    session.retrieval_status = "abandoned"
    session.ended_at = datetime.now(timezone.utc)
    if session.mode == "research":
        from app.services import upload_service
        upload_service.cleanup_research_session_files(session_id)
    return session
