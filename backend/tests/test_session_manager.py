import pytest
from app.models.clue import Clue
from app.models.image import ImageProfile
from app.models.candidate import CandidateEntry
from app.models.session import RetrievalSession
from app.services import session_manager


@pytest.fixture(autouse=True)
def cleanup_sessions():
    session_manager.clear_all_sessions()
    yield
    session_manager.clear_all_sessions()


def test_1_create_demo_session():
    """1. Create Demo session."""
    session = session_manager.create_session(mode="demo")
    assert session.session_id.startswith("sess_")
    assert session.mode == "demo"
    assert session.retrieval_status == "created"


def test_2_create_research_session():
    """2. Create Research session."""
    session = session_manager.create_session(mode="research")
    assert session.mode == "research"
    assert session.retrieval_status == "created"


def test_3_reject_invalid_session_mode():
    """3. Reject invalid session mode."""
    with pytest.raises(session_manager.InvalidSessionModeError):
        session_manager.create_session(mode="invalid_mode")


def test_4_retrieval_session_mutable_fields_isolation():
    """4. RetrievalSession mutable fields are isolated between instances."""
    s1 = session_manager.create_session(mode="demo")
    s2 = session_manager.create_session(mode="research")

    s1.clues.append(Clue(dimension="clothing", value="pink", source="user_initial", certainty="definite"))
    s1.dimensions_asked.add("setting")
    s1.explicitly_rejected_ids.add("img_001")

    assert len(s1.clues) == 1
    assert len(s2.clues) == 0

    assert "setting" in s1.dimensions_asked
    assert "setting" not in s2.dimensions_asked

    assert "img_001" in s1.explicitly_rejected_ids
    assert "img_001" not in s2.explicitly_rejected_ids


def test_5_add_definite_user_clue():
    """5. Add definite user clue."""
    session = session_manager.create_session(mode="demo")
    clue = Clue(
        dimension="clothing",
        value="pink dress",
        source="user_initial",
        certainty="definite",
        subattribute_key="clothing:pink_dress",
    )
    session_manager.add_clue(session.session_id, clue)

    updated = session_manager.get_session(session.session_id)
    assert len(updated.clues) == 1
    assert updated.clues[0].dimension == "clothing"
    assert updated.clues[0].certainty == "definite"
    assert updated.clues[0].source == "user_initial"
    assert "clothing" in updated.dimensions_provided_by_user


def test_6_add_inferred_clue_preserve_inferred_source_certainty():
    """6. Add inferred clue and preserve inferred source/certainty."""
    session = session_manager.create_session(mode="demo")
    clue = Clue(
        dimension="occasion",
        value="birthday",
        source="inferred",
        certainty="inferred",
    )
    session_manager.add_clue(session.session_id, clue)

    updated = session_manager.get_session(session.session_id)
    assert len(updated.clues) == 1
    assert updated.clues[0].source == "inferred"
    assert updated.clues[0].certainty == "inferred"


def test_7_mark_dimension_as_asked():
    """7. Mark dimension as asked."""
    session = session_manager.create_session(mode="demo")
    session_manager.mark_dimension_asked(session.session_id, "setting")

    updated = session_manager.get_session(session.session_id)
    assert "setting" in updated.dimensions_asked


def test_8_mark_subattribute_as_asked():
    """8. Mark subattribute as asked."""
    session = session_manager.create_session(mode="demo")
    session_manager.mark_subattribute_asked(session.session_id, "objects:cake")

    updated = session_manager.get_session(session.session_id)
    assert "objects:cake" in updated.subattributes_asked


def test_9_idk_increments_both_counters():
    """9. IDK increments both counters (consecutive_idk_count and total_idk_count)."""
    session = session_manager.create_session(mode="demo")
    session_manager.record_idk(session.session_id)
    session_manager.record_idk(session.session_id)

    updated = session_manager.get_session(session.session_id)
    assert updated.consecutive_idk_count == 2
    assert updated.total_idk_count == 2


def test_10_valid_answer_resets_consecutive_idk_count_not_total_idk():
    """10. A valid answer resets consecutive_idk_count but NOT total_idk_count."""
    session = session_manager.create_session(mode="demo")
    session_manager.record_idk(session.session_id)
    session_manager.record_idk(session.session_id)

    # Valid answer occurs
    session_manager.reset_consecutive_idk(session.session_id)

    updated = session_manager.get_session(session.session_id)
    assert updated.consecutive_idk_count == 0
    assert updated.total_idk_count == 2  # Lifetime total preserved for analytics!


def test_11_reject_candidate_removes_candidate_from_active_pool():
    """11. Reject candidate removes candidate from active pool."""
    session = session_manager.create_session(mode="demo")

    p1 = ImageProfile(image_id="img_001", free_description="Photo 1")
    p2 = ImageProfile(image_id="img_002", free_description="Photo 2")

    c1 = CandidateEntry(image_id="img_001", score=8.0, profile=p1, pool="active")
    c2 = CandidateEntry(image_id="img_002", score=7.0, profile=p2, pool="active")

    session_manager.set_candidate_pools(session.session_id, active=[c1, c2], reserve=[])

    # Reject img_001
    session_manager.reject_candidate_ids(session.session_id, ["img_001"])

    updated = session_manager.get_session(session.session_id)
    assert "img_001" in updated.explicitly_rejected_ids
    assert len(updated.active_candidates) == 1
    assert updated.active_candidates[0].image_id == "img_002"


def test_12_rejected_candidate_cannot_accidentally_return_to_active_pool():
    """12. Rejected candidate cannot accidentally return to active pool."""
    session = session_manager.create_session(mode="demo")
    session_manager.reject_candidate_ids(session.session_id, ["img_001"])

    p1 = ImageProfile(image_id="img_001", free_description="Photo 1")
    p2 = ImageProfile(image_id="img_002", free_description="Photo 2")

    c1 = CandidateEntry(image_id="img_001", score=9.5, profile=p1, pool="active")
    c2 = CandidateEntry(image_id="img_002", score=7.0, profile=p2, pool="active")

    # Attempt to set pools including rejected img_001
    session_manager.set_candidate_pools(session.session_id, active=[c1, c2], reserve=[])

    updated = session_manager.get_session(session.session_id)
    active_ids = [c.image_id for c in updated.active_candidates]
    assert "img_001" not in active_ids
    assert "img_002" in active_ids


def test_13_session_found_state_stores_final_target_id_and_ended_at():
    """13. Session found state stores final_target_id and ended_at."""
    session = session_manager.create_session(mode="demo")
    session_manager.mark_found(session.session_id, final_target_id="img_042")

    updated = session_manager.get_session(session.session_id)
    assert updated.retrieval_status == "found"
    assert updated.final_target_id == "img_042"
    assert updated.ended_at is not None


def test_14_session_unresolved_state_stores_ended_at():
    """14. Session unresolved state stores ended_at."""
    session = session_manager.create_session(mode="demo")
    session_manager.mark_unresolved(session.session_id)

    updated = session_manager.get_session(session.session_id)
    assert updated.retrieval_status == "unresolved"
    assert updated.ended_at is not None
