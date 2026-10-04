from __future__ import annotations
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, status, UploadFile, File, Header
from fastapi.responses import JSONResponse

logger = logging.getLogger("memory_guide.sessions_route")

from app.models.api import (
    CreateSessionRequest,
    QueryRequest,
    AnswerRequest,
    SelectRequest,
    SessionSummaryResponseData,
    APIResponse,
)
from app.models.clue import Clue
from app.models.candidate import CandidateEntry
from app.models.session import CandidateHistoryEntry, QuestionAnswerRecord
from app.config import settings
from app.services import (
    session_manager,
    upload_service,
    library_service,
    image_understanding_service,
    query_parser,
    embedding_service,
    candidate_retriever,
    gemini_client,
    discrimination,
    question_generator,
    answer_interpreter,
    analytics_db,
)
from app.services.synthetic_vectors import generate_deterministic_synthetic_vector

router = APIRouter()

MAX_ROUNDS = 5


def format_candidate_for_recognition(c: CandidateEntry, rank: int, session_id: str) -> Dict[str, Any]:
    """Helper to format candidate for recognition display."""
    lib_item = library_service.get_library_image(session_id, c.image_id)
    url = lib_item.image_url if lib_item else f"/images/demo-photos/{c.image_id}.jpg"
    return {
        "imageId": c.image_id,
        "rank": rank,
        "score": c.score,
        "semanticScore": c.semantic_score,
        "structuredScore": c.structured_score,
        "imageUrl": url,
    }


def helper_rescore_and_partition(sessionId: str) -> Tuple[List[CandidateEntry], List[CandidateEntry]]:
    """Helper to rescore all non-rejected candidates and partition into active/reserve pools."""
    session = session_manager.get_session(sessionId)
    if not session:
        return [], []

    # Get query embedding
    has_api_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key")
    query_vec = None
    if has_api_key and session.original_query:
        try:
            query_vec = gemini_client.embed_text(session.original_query)
        except Exception as e:
            if not settings.ALLOW_SYNTHETIC_AI:
                raise e
            logger.warning(f"Live embedding API call failed: {e}. Falling back to synthetic vector.")
            query_vec = None

    if not query_vec:
        query_vec = generate_deterministic_synthetic_vector(session.original_query or "vague query")

    embeddings_map = embedding_service.get_session_embeddings(sessionId)
    profiles_list = image_understanding_service.get_session_profiles(sessionId)
    profiles_map = {prof.image_id: prof for prof in profiles_list}

    existing_candidate_ids = {c.image_id for c in (session.active_candidates + session.reserve_candidates)}
    if existing_candidate_ids:
        active_embeddings = {
            img_id: vec for img_id, vec in embeddings_map.items()
            if img_id in existing_candidate_ids and img_id not in session.explicitly_rejected_ids
        }
    else:
        active_embeddings = {
            img_id: vec for img_id, vec in embeddings_map.items()
            if img_id not in session.explicitly_rejected_ids
        }

    ranked_results = candidate_retriever.rank_candidates_composite(
        query_embedding=query_vec,
        image_embeddings=active_embeddings,
        image_profiles=profiles_map,
        clues=session.clues,
    )

    top_score = ranked_results[0][1] if ranked_results else 0.0
    initial_limit = getattr(settings, "INITIAL_ACTIVE_LIMIT", 12)

    if session.clues and len(session.clues) > 0 and top_score > 0:
        qualifying_count = sum(1 for _, s, _, _ in ranked_results if (top_score - s) <= 0.12)
        active_limit = max(3, min(initial_limit, qualifying_count))
    else:
        active_limit = initial_limit

    active_entries: List[CandidateEntry] = []
    reserve_entries: List[CandidateEntry] = []

    for rank_idx, (img_id, final_score, sem_score, struct_score) in enumerate(ranked_results, start=1):
        is_active = (rank_idx <= active_limit)
        entry = CandidateEntry(
            image_id=img_id,
            score=round(final_score, 4),
            semantic_score=round(sem_score, 4),
            structured_score=round(struct_score, 4),
            pool="active" if is_active else "reserve",
            profile=profiles_map[img_id].model_dump() if img_id in profiles_map else None,
        )
        if is_active:
            active_entries.append(entry)
        else:
            reserve_entries.append(entry)

    session_manager.set_candidate_pools(sessionId, active_entries, reserve_entries)
    return active_entries, reserve_entries


@router.post("/sessions", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def create_retrieval_session(payload: CreateSessionRequest):
    """
    Creates a new retrieval session in either 'demo' or 'research' mode.
    """
    try:
        session = session_manager.create_session(mode=payload.mode)
        return APIResponse(
            success=True,
            data={
                "sessionId": session.session_id,
                "mode": session.mode,
                "status": session.retrieval_status,
            },
            error=None,
        )
    except session_manager.InvalidSessionModeError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "INVALID_MODE", "message": str(e)},
            ).model_dump(),
        )


@router.get("/sessions/{sessionId}", response_model=APIResponse)
async def get_retrieval_session(sessionId: str):
    """
    Returns non-sensitive session summary metadata for development and debugging.
    """
    session = session_manager.get_session(sessionId)
    if not session:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "SESSION_NOT_FOUND", "message": f"Session '{sessionId}' not found."},
            ).model_dump(),
        )

    image_count = library_service.get_library_image_count(sessionId)

    summary = SessionSummaryResponseData(
        sessionId=session.session_id,
        mode=session.mode,
        status=session.retrieval_status,
        startedAt=session.started_at.isoformat(),
        cluesCount=len(session.clues),
        activeCandidateCount=len(session.active_candidates),
        reserveCandidateCount=len(session.reserve_candidates),
        rejectedCandidateCount=len(session.explicitly_rejected_ids),
        roundCount=session.round_count,
        consecutiveIdkCount=session.consecutive_idk_count,
        totalIdkCount=session.total_idk_count,
    )

    data_dict = summary.model_dump()
    data_dict["imageCount"] = image_count

    return APIResponse(
        success=True,
        data=data_dict,
        error=None,
    )


@router.post("/sessions/{sessionId}/upload", response_model=APIResponse)
async def upload_research_photos(sessionId: str, files: List[UploadFile] = File(...)):
    """
    Uploads a batch of personal research photos for a Research Mode session.
    """
    try:
        saved_images = await upload_service.save_research_uploads(sessionId, files)
        image_understanding_service.index_research_library(sessionId)
        embedding_service.index_research_embeddings(sessionId)

        session = session_manager.get_session(sessionId)
        current_status = session.retrieval_status if session else "ready"
        total_count = library_service.get_library_image_count(sessionId)

        return APIResponse(
            success=True,
            data={
                "uploadedCount": len(saved_images),
                "imageCount": total_count,
                "status": current_status,
                "message": f"{len(saved_images)} photos ready for your retrieval session."
            },
            error=None,
        )
    except upload_service.UploadValidationError as e:
        status_code = status.HTTP_404_NOT_FOUND if e.code == "SESSION_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        return JSONResponse(
            status_code=status_code,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": e.code, "message": e.message},
            ).model_dump(),
        )


@router.get("/sessions/{sessionId}/library", response_model=APIResponse)
async def get_session_library_debug(sessionId: str):
    """
    [DEVELOPMENT / DEBUGGING ONLY] Lists non-sensitive library asset metadata.
    """
    session = session_manager.get_session(sessionId)
    if not session:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "SESSION_NOT_FOUND", "message": f"Session '{sessionId}' not found."},
            ).model_dump(),
        )

    lib = library_service.get_library(sessionId)
    items = [
        {
            "imageId": img.image_id,
            "source": img.source,
            "storedFilename": img.stored_filename,
            "contentType": img.content_type,
            "fileSize": img.file_size,
            "imageUrl": img.image_url,
        }
        for img in lib
    ]

    return APIResponse(
        success=True,
        data={
            "sessionId": sessionId,
            "mode": session.mode,
            "imageCount": len(items),
            "images": items,
        },
        error=None,
    )


@router.get("/sessions/{sessionId}/profiles", response_model=APIResponse)
async def get_session_profiles_debug(sessionId: str):
    """
    [DEVELOPMENT / DEBUGGING ONLY] Lists ImageProfiles for session library.
    """
    session = session_manager.get_session(sessionId)
    if not session:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "SESSION_NOT_FOUND", "message": f"Session '{sessionId}' not found."},
            ).model_dump(),
        )

    profiles = image_understanding_service.get_session_profiles(sessionId)
    items = [prof.model_dump() for prof in profiles]

    return APIResponse(
        success=True,
        data={
            "sessionId": sessionId,
            "mode": session.mode,
            "status": session.retrieval_status,
            "profileCount": len(items),
            "profiles": items,
        },
        error=None,
    )


@router.post("/sessions/{sessionId}/query", response_model=APIResponse)
async def query_initial_description(sessionId: str, payload: QueryRequest):
    """
    Accepts initial vague-memory query text, parses clues, embeds query, ranks candidates,
    runs candidate-aware discrimination, and returns EITHER next adaptive question OR recognition set.
    """
    session = session_manager.get_session(sessionId)
    if not session:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "SESSION_NOT_FOUND", "message": f"Session '{sessionId}' not found."},
            ).model_dump(),
        )

    if not payload.query or not payload.query.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "EMPTY_QUERY", "message": "Query string cannot be empty or whitespace."},
            ).model_dump(),
        )

    if session.mode == "research":
        research_imgs = library_service.get_research_library(sessionId)
        if not research_imgs:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=APIResponse(
                    success=False,
                    data=None,
                    error={"code": "LIBRARY_EMPTY", "message": "Research mode library has no uploaded photos."},
                ).model_dump(),
            )

    # Reset/set query state
    session.original_query = payload.query.strip()
    session.clues.clear()
    session.dimensions_asked.clear()
    session.subattributes_asked.clear()
    session.dimensions_provided_by_user.clear()

    # Parse initial clues
    clues = query_parser.parse_query_to_clues(session.original_query)
    for clue in clues:
        session_manager.add_clue(sessionId, clue)
        session.dimensions_provided_by_user.add(clue.dimension)

    try:
        # Initial rescore & pool partitioning
        try:
            active_entries, reserve_entries = helper_rescore_and_partition(sessionId)
        except gemini_client.GeminiAPIError as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=APIResponse(
                    success=False,
                    data=None,
                    error={"code": "EMBEDDING_PROVIDER_ERROR", "message": f"Embedding provider error and synthetic fallback is disabled: {str(e)}"},
                ).model_dump(),
            )

        # Record CandidateHistoryEntry
        session.candidate_history.append(CandidateHistoryEntry(
            round=0,
            trigger="initial_retrieval",
            active_count=len(active_entries),
            reserve_count=len(reserve_entries),
            rejected_count=len(session.explicitly_rejected_ids),
        ))

        session.retrieval_status = "in_progress"

        # Select next question via Discrimination Engine
        selection = discrimination.select_next_best_question(session)

        # Determine whether to ask question or show candidates
        if selection and len(active_entries) > 6 and session.round_count < MAX_ROUNDS:
            session.round_count = 1
            question = question_generator.generate_clarification_question(selection, session.round_count)
            session.current_question = question

            return APIResponse(
                success=True,
                data={
                    "action": "ask_question",
                    "question": {
                        "questionId": question.question_id,
                        "round": question.round,
                        "text": question.text,
                        "options": question.options,
                        "dimensionTested": question.dimension_tested,
                        "subattributeKey": question.subattribute_key,
                    },
                    "progress": {
                        "activeCandidates": len(active_entries),
                        "reserveCandidates": len(reserve_entries),
                        "round": session.round_count,
                    },
                },
                error=None,
            )

        # Show Recognition Candidates
        return build_recognition_candidate_response(sessionId, active_entries, reserve_entries, session.round_count)
    except Exception as e:
        logger.error(f"Error in query_initial_description for session {sessionId}: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "QUERY_ERROR", "message": f"Query processing failed: {str(e)}"},
            ).model_dump(),
        )
def build_recognition_candidate_response(sessionId: str, active_entries: List[CandidateEntry], reserve_entries: List[CandidateEntry], round_count: int) -> APIResponse:
    """Formats top 3-6 recognition candidates from the latest complete non-rejected ranking (active + reserve)."""
    session = session_manager.get_session(sessionId)
    if session:
        session.retrieval_status = "showing_candidates"

    all_non_rejected = sorted(active_entries + reserve_entries, key=lambda c: c.score, reverse=True)
    top_rec = [
        format_candidate_for_recognition(c, i + 1, sessionId)
        for i, c in enumerate(all_non_rejected[:6])
    ]
    return APIResponse(
        success=True,
        data={
            "action": "show_candidates",
            "candidates": top_rec,
            "progress": {
                "activeCandidates": len(active_entries),
                "reserveCandidates": len(reserve_entries),
                "round": round_count,
            },
        },
        error=None,
    )


@router.post("/sessions/{sessionId}/answer", response_model=APIResponse)
async def answer_question(sessionId: str, payload: AnswerRequest):
    """
    Accepts user answer to current clarification question, interprets clue, safely rescores candidates,
    and returns EITHER next adaptive question OR visual recognition candidates.
    """
    session = session_manager.get_session(sessionId)
    if not session:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "SESSION_NOT_FOUND", "message": f"Session '{sessionId}' not found."},
            ).model_dump(),
        )

    if not session.current_question:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "NO_ACTIVE_QUESTION", "message": "No active question to answer in this session."},
            ).model_dump(),
        )

    question = session.current_question
    cand_before = len(session.active_candidates)

    # Interpret user answer
    is_idk, clue = answer_interpreter.interpret_user_answer(question, payload.answerText)

    # Mark dimension / subattribute as asked
    session.dimensions_asked.add(question.dimension_tested)
    if question.subattribute_key:
        session.subattributes_asked.add(question.subattribute_key)

    if is_idk:
        session.consecutive_idk_count += 1
        session.total_idk_count += 1
        # IDK: No clue added, no candidate rescoring or pool changes
        active_entries = session.active_candidates
        reserve_entries = session.reserve_candidates
    else:
        session.consecutive_idk_count = 0
        if clue:
            session.clues.append(clue)
        # Rescore ALL non-rejected candidates (active and reserve)
        active_entries, reserve_entries = helper_rescore_and_partition(sessionId)

    cand_after = len(active_entries)

    # Record QuestionAnswerRecord
    meta = question.selection_metadata
    session.question_history.append(QuestionAnswerRecord(
        question_id=question.question_id,
        round=question.round,
        dimension=question.dimension_tested,
        subattribute_key=question.subattribute_key,
        question_text=question.text,
        answer_text=payload.answerText,
        parsed_value=clue.value if clue else None,
        answer_certainty=clue.certainty if clue else None,
        was_idk=is_idk,
        candidates_before=cand_before,
        candidates_after=cand_after,
        discrimination_score=meta.discrimination_score if meta else None,
        final_question_score=meta.final_score if meta else None,
    ))

    # Record CandidateHistoryEntry
    session.candidate_history.append(CandidateHistoryEntry(
        round=session.round_count,
        trigger=f"question:{question.subattribute_key or question.dimension_tested}",
        active_count=len(active_entries),
        reserve_count=len(reserve_entries),
        rejected_count=len(session.explicitly_rejected_ids),
    ))

    session.current_question = None

    # Check Termination Rules (Requirement 13)
    top_gap = 0.0
    if len(active_entries) >= 2:
        top_gap = active_entries[0].score - active_entries[1].score

    terminate = False
    if len(active_entries) <= 6:
        terminate = True
    elif top_gap >= 0.15:
        terminate = True
    elif session.round_count >= MAX_ROUNDS:
        terminate = True
    elif session.consecutive_idk_count >= 3:
        terminate = True

    if not terminate:
        selection = discrimination.select_next_best_question(session)
        if selection:
            session.round_count += 1
            next_q = question_generator.generate_clarification_question(selection, session.round_count)
            session.current_question = next_q

            return APIResponse(
                success=True,
                data={
                    "action": "ask_question",
                    "question": {
                        "questionId": next_q.question_id,
                        "round": next_q.round,
                        "text": next_q.text,
                        "options": next_q.options,
                        "dimensionTested": next_q.dimension_tested,
                        "subattributeKey": next_q.subattribute_key,
                    },
                    "progress": {
                        "activeCandidates": len(active_entries),
                        "reserveCandidates": len(reserve_entries),
                        "round": session.round_count,
                    },
                },
                error=None,
            )

    # Show Recognition Candidates
    return build_recognition_candidate_response(sessionId, active_entries, reserve_entries, session.round_count)


@router.post("/sessions/{sessionId}/select", response_model=APIResponse)
async def select_candidate(sessionId: str, payload: SelectRequest):
    """
    Handles user interaction during candidate recognition:
    - 'found': Target confirmed by user ("This is it"). Persists session analytics.
    - 'none': None of shown candidates match. Permanently rejects ONLY shown candidate IDs and resumes retrieval.
    - 'close': User picks a close photo as positive reference. Asks targeted follow-up question.
    """
    session = session_manager.get_session(sessionId)
    if not session:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "SESSION_NOT_FOUND", "message": f"Session '{sessionId}' not found."},
            ).model_dump(),
        )

    stype = payload.selectionType.lower().strip()

    if stype == "found":
        if not payload.imageId:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=APIResponse(
                    success=False,
                    data=None,
                    error={"code": "MISSING_IMAGE_ID", "message": "imageId is required when selectionType='found'."},
                ).model_dump(),
            )

        session.final_target_id = payload.imageId
        session.retrieval_status = "found"
        session.ended_at = datetime.now(timezone.utc)

        # Persist session analytics to DB
        analytics_db.record_session_analytics(session)

        # Clean up research files if research mode
        if session.mode == "research":
            embedding_service.clear_research_embeddings(sessionId)

        return APIResponse(
            success=True,
            data={
                "action": "found",
                "sessionId": sessionId,
                "targetId": payload.imageId,
                "status": session.retrieval_status,
                "message": "Target photo successfully identified!",
            },
            error=None,
        )

    elif stype == "none":
        # Permanently reject ONLY shown candidate IDs (NO negative attribute transfer)
        rejected_ids = payload.rejectedImageIds or [c.image_id for c in session.active_candidates[:6]]
        for r_id in rejected_ids:
            session.explicitly_rejected_ids.add(r_id)

        # Rescore and partition remaining candidates
        active_entries, reserve_entries = helper_rescore_and_partition(sessionId)

        session.candidate_history.append(CandidateHistoryEntry(
            round=session.round_count,
            trigger="select:none",
            active_count=len(active_entries),
            reserve_count=len(reserve_entries),
            rejected_count=len(session.explicitly_rejected_ids),
        ))

        # Check next action: ask question or show next candidate set
        selection = discrimination.select_next_best_question(session)
        if selection and len(active_entries) > 6 and session.round_count < MAX_ROUNDS:
            session.round_count += 1
            next_q = question_generator.generate_clarification_question(selection, session.round_count)
            session.current_question = next_q

            return APIResponse(
                success=True,
                data={
                    "action": "ask_question",
                    "question": {
                        "questionId": next_q.question_id,
                        "round": next_q.round,
                        "text": next_q.text,
                        "options": next_q.options,
                        "dimensionTested": next_q.dimension_tested,
                        "subattributeKey": next_q.subattribute_key,
                    },
                    "progress": {
                        "activeCandidates": len(active_entries),
                        "reserveCandidates": len(reserve_entries),
                        "round": session.round_count,
                    },
                },
                error=None,
            )
        else:
            return build_recognition_candidate_response(sessionId, active_entries, reserve_entries, session.round_count)

    elif stype == "close":
        if not payload.imageId:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=APIResponse(
                    success=False,
                    data=None,
                    error={"code": "MISSING_IMAGE_ID", "message": "imageId is required when selectionType='close'."},
                ).model_dump(),
            )

        ref_id = payload.imageId
        profiles_list = image_understanding_service.get_session_profiles(sessionId)
        profiles_map = {p.image_id: p for p in profiles_list}
        ref_prof = profiles_map.get(ref_id)

        # Use close photo as positive reference
        if ref_prof:
            # Boost candidate agreement based on reference profile attributes
            ref_clues = []
            if ref_prof.setting:
                ref_clues.append(Clue(dimension="setting", value=ref_prof.setting, source="inferred", certainty="probable"))
            if ref_prof.occasion:
                ref_clues.append(Clue(dimension="occasion", value=ref_prof.occasion, source="inferred", certainty="probable"))
            for cl in ref_clues:
                session.clues.append(cl)

        active_entries, reserve_entries = helper_rescore_and_partition(sessionId)

        selection = discrimination.select_next_best_question(session)
        if selection:
            session.round_count += 1
            next_q = question_generator.generate_clarification_question(selection, session.round_count)
            session.current_question = next_q

            return APIResponse(
                success=True,
                data={
                    "action": "ask_question",
                    "question": {
                        "questionId": next_q.question_id,
                        "round": next_q.round,
                        "text": next_q.text,
                        "options": next_q.options,
                        "dimensionTested": next_q.dimension_tested,
                        "subattributeKey": next_q.subattribute_key,
                    },
                    "progress": {
                        "activeCandidates": len(active_entries),
                        "reserveCandidates": len(reserve_entries),
                        "round": session.round_count,
                    },
                },
                error=None,
            )
        else:
            return build_recognition_candidate_response(sessionId, active_entries, reserve_entries, session.round_count)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=APIResponse(
            success=False,
            data=None,
            error={"code": "INVALID_SELECTION_TYPE", "message": f"Unknown selectionType '{payload.selectionType}'."},
        ).model_dump(),
    )


@router.post("/sessions/{sessionId}/feedback", response_model=APIResponse)
async def submit_session_feedback(sessionId: str, payload: Dict[str, Any]):
    """
    Submits user helpfulness rating and qualitative feedback for a session.
    """
    session = session_manager.get_session(sessionId)
    if not session:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "SESSION_NOT_FOUND", "message": f"Session '{sessionId}' not found."},
            ).model_dump(),
        )

    rating = payload.get("helpfulnessRating")
    feedback_text = payload.get("confusingFeedback")

    session.question_helpfulness_rating = rating
    session.qualitative_feedback = feedback_text

    try:
        analytics_db.record_session_analytics(session)
    except Exception as e:
        logger.warning(f"Error persisting feedback analytics: {e}")

    return APIResponse(
        success=True,
        data={"recorded": True, "sessionId": sessionId},
        error=None,
    )


@router.get("/analytics/export", response_model=APIResponse)
async def export_analytics_data(
    token: Optional[str] = None,
    x_admin_token: Optional[str] = Header(None, alias="x-admin-token"),
):
    """
    [SECURED] Exports all research_sessions analytics records.
    Requires valid admin token via 'x-admin-token' header or 'token' query parameter.
    """
    provided_token = x_admin_token or token
    if not provided_token or provided_token != settings.ANALYTICS_ADMIN_TOKEN:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "UNAUTHORIZED", "message": "Invalid or missing admin token."},
            ).model_dump(),
        )

    exported_rows = analytics_db.export_all_sessions()
    return APIResponse(
        success=True,
        data={"sessions": exported_rows, "totalCount": len(exported_rows)},
        error=None,
    )

