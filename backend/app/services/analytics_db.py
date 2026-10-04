import os
import sqlite3
import logging
from app.config import settings

logger = logging.getLogger("memory_guide.analytics_db")


def init_db(db_path: str = None) -> None:
    """
    Creates the SQLite database file (and its directory) if needed,
    and initializes the research_sessions schema.
    """
    target_path = db_path or settings.DB_PATH
    
    # Ensure database directory exists
    db_dir = os.path.dirname(os.path.abspath(target_path))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        logger.info(f"Created database directory: {db_dir}")

    logger.info(f"Initializing SQLite database at: {target_path}")

    with sqlite3.connect(target_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_sessions (
                session_id TEXT PRIMARY KEY,
                started_at TEXT,
                ended_at TEXT,
                library_mode TEXT,
                retrieval_status TEXT,
                original_description TEXT,
                total_time_seconds INTEGER,
                questions_to_target INTEGER,
                total_idk_count INTEGER,
                candidate_reduction_json TEXT,
                clues_json TEXT,
                questions_answers_json TEXT,
                final_target_id TEXT,
                question_helpfulness_rating INTEGER,
                qualitative_feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    logger.info("Database schema initialized successfully.")


def record_session_analytics(session, db_path: str = None) -> None:
    """
    Persists or updates session analytics in the SQLite research_sessions table.
    """
    import json
    target_path = db_path or settings.DB_PATH
    init_db(target_path)

    started_at_str = session.started_at.isoformat() if getattr(session, "started_at", None) else None
    ended_at_str = session.ended_at.isoformat() if getattr(session, "ended_at", None) else None

    total_time = None
    if getattr(session, "started_at", None) and getattr(session, "ended_at", None):
        total_time = int((session.ended_at - session.started_at).total_seconds())

    orig_desc = session.query_history[0] if getattr(session, "query_history", None) else ""
    clues_data = [c.model_dump() if hasattr(c, "model_dump") else c for c in getattr(session, "clues", [])]
    q_data = [q.model_dump() if hasattr(q, "model_dump") else q for q in getattr(session, "question_history", [])]

    with sqlite3.connect(target_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO research_sessions (
                session_id, started_at, ended_at, library_mode, retrieval_status,
                original_description, total_time_seconds, questions_to_target,
                total_idk_count, candidate_reduction_json, clues_json,
                questions_answers_json, final_target_id, question_helpfulness_rating,
                qualitative_feedback
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.session_id,
            started_at_str,
            ended_at_str,
            getattr(session, "mode", "demo"),
            getattr(session, "retrieval_status", "active"),
            orig_desc,
            total_time,
            len(getattr(session, "question_history", [])),
            getattr(session, "total_idk_count", 0),
            json.dumps(getattr(session, "candidate_reduction_history", []), default=str),
            json.dumps(clues_data, default=str),
            json.dumps(q_data, default=str),
            getattr(session, "final_target_id", None),
            getattr(session, "question_helpfulness_rating", None),
            getattr(session, "qualitative_feedback", None)
        ))
        conn.commit()
    logger.info(f"Persisted session analytics for session {session.session_id}")


def export_all_sessions(db_path: str = None) -> list[dict]:
    """
    Returns all research_sessions records as a list of dictionaries.
    """
    target_path = db_path or settings.DB_PATH
    init_db(target_path)
    with sqlite3.connect(target_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM research_sessions ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


