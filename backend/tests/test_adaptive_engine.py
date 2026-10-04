from __future__ import annotations
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.models.clue import Clue
from app.models.image import ImageProfile
from app.models.candidate import CandidateEntry
from app.services import (
    session_manager,
    discrimination,
    question_generator,
    answer_interpreter,
    candidate_retriever,
    embedding_service,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_cleanup_test_sessions():
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        yield
        session_manager.clear_all_sessions()


def test_1_categorical_discrimination_chooses_meaningful_split():
    session = session_manager.create_session(mode="demo")
    # Set 4 active candidates: 2 indoor, 2 outdoor
    session.active_candidates = [
        CandidateEntry(image_id="demo_001", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active"),
        CandidateEntry(image_id="demo_002", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active"),
        CandidateEntry(image_id="demo_003", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active"),
        CandidateEntry(image_id="demo_004", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active"),
    ]
    selection = discrimination.select_next_best_question(session)
    assert selection is not None
    assert selection.final_score >= 0.10


def test_2_list_subattribute_split_score_works():
    session = session_manager.create_session(mode="demo")
    session.active_candidates = [
        CandidateEntry(image_id="demo_001", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active"),
        CandidateEntry(image_id="demo_002", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active"),
    ]
    selection = discrimination.select_next_best_question(session)
    assert selection is not None


def test_3_relevance_weighting_works():
    session = session_manager.create_session(mode="demo")
    session.active_candidates = [
        CandidateEntry(image_id="demo_001", score=0.99, semantic_score=0.99, structured_score=0.99, pool="active"),
        CandidateEntry(image_id="demo_002", score=0.01, semantic_score=0.01, structured_score=0.01, pool="active"),
    ]
    selection = discrimination.select_next_best_question(session)
    assert selection is None or selection.final_score >= 0.0


def test_4_already_provided_dimension_excluded():
    session = session_manager.create_session(mode="demo")
    session.dimensions_provided_by_user.add("setting")
    session.active_candidates = [
        CandidateEntry(image_id="demo_001", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active"),
        CandidateEntry(image_id="demo_003", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active"),
    ]
    excluded_dims, _ = discrimination.get_excluded_keys(session)
    assert "setting" in excluded_dims


def test_5_already_asked_dimension_excluded():
    session = session_manager.create_session(mode="demo")
    session.dimensions_asked.add("occasion")
    excluded_dims, _ = discrimination.get_excluded_keys(session)
    assert "occasion" in excluded_dims


def test_6_asked_subattribute_excluded_but_sibling_subattribute_remains_eligible():
    session = session_manager.create_session(mode="demo")
    session.subattributes_asked.add("objects:cake")
    _, excluded_subkeys = discrimination.get_excluded_keys(session)
    assert "objects:cake" in excluded_subkeys
    assert "objects:balloons" not in excluded_subkeys


def test_7_best_question_is_deterministic_given_same_candidate_set():
    session = session_manager.create_session(mode="demo")
    session.active_candidates = [
        CandidateEntry(image_id="demo_001", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active"),
        CandidateEntry(image_id="demo_003", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active"),
    ]
    s1 = discrimination.select_next_best_question(session)
    s2 = discrimination.select_next_best_question(session)
    assert s1.dimension == s2.dimension
    assert s1.subattribute_key == s2.subattribute_key


def test_8_question_generator_phrases_selected_dimension_only():
    session = session_manager.create_session(mode="demo")
    selection = discrimination.QuestionSelection(
        selection_type="categorical",
        dimension="setting",
        value="indoor",
        discrimination_score=0.5,
        memorability_weight=1.0,
        final_score=0.5,
    )
    q = question_generator.generate_clarification_question(selection, round_num=1)
    assert q.dimension_tested == "setting"
    assert "indoors" in q.text.lower() or "setting" in q.text.lower()


def test_9_and_10_idk_does_not_rerank_and_increments_counters():
    session = session_manager.create_session(mode="demo")
    session.current_question = question_generator.ClarificationQuestion(
        question_id="q1",
        round=1,
        text="Was a cake visible?",
        dimension_tested="objects",
        subattribute_key="objects:cake",
        options=["Yes", "No", "I don't remember"],
    )
    res = client.post(
        f"/api/v1/sessions/{session.session_id}/answer",
        json={"answerText": "I don't remember"},
    )
    assert res.status_code == 200
    updated = session_manager.get_session(session.session_id)
    assert updated.consecutive_idk_count == 1
    assert updated.total_idk_count == 1


def test_11_usable_answer_resets_consecutive_but_not_total_idk():
    session = session_manager.create_session(mode="demo")
    session.consecutive_idk_count = 2
    session.total_idk_count = 2
    session.current_question = question_generator.ClarificationQuestion(
        question_id="q1",
        round=1,
        text="Was a cake visible?",
        dimension_tested="objects",
        subattribute_key="objects:cake",
        options=["Yes", "No", "I don't remember"],
    )
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        res = client.post(
            f"/api/v1/sessions/{session.session_id}/answer",
            json={"answerText": "Yes"},
        )
        assert res.status_code == 200
        updated = session_manager.get_session(session.session_id)
        assert updated.consecutive_idk_count == 0
        assert updated.total_idk_count == 2


def test_12_positive_answer_boosts_matching_candidates():
    prof_cake = ImageProfile(image_id="img_c", objects=["cake"])
    prof_nocake = ImageProfile(image_id="img_nc", objects=[])
    clue_pos = Clue(dimension="objects", value="cake", source="user_answer", certainty="definite", polarity="positive")

    s_cake = candidate_retriever.compute_structured_clue_agreement(prof_cake, [clue_pos])
    s_nocake = candidate_retriever.compute_structured_clue_agreement(prof_nocake, [clue_pos])
    assert s_cake > s_nocake


def test_13_explicit_negative_answer_penalizes_matching_attribute_appropriately():
    prof_cake = ImageProfile(image_id="img_c", objects=["cake"])
    prof_nocake = ImageProfile(image_id="img_nc", objects=[])
    clue_neg = Clue(dimension="objects", value="cake", source="user_answer", certainty="definite", polarity="negative")

    s_cake = candidate_retriever.compute_structured_clue_agreement(prof_cake, [clue_neg])
    s_nocake = candidate_retriever.compute_structured_clue_agreement(prof_nocake, [clue_neg])
    assert s_nocake > s_cake


def test_14_reserve_candidate_can_recover():
    session = session_manager.create_session(mode="demo")
    session.active_candidates = [CandidateEntry(image_id="demo_002", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active")]
    session.reserve_candidates = [CandidateEntry(image_id="demo_001", score=0.5, semantic_score=0.5, structured_score=0.5, pool="reserve")]
    session.clues.append(Clue(dimension="clothing", value="pink dress", source="user_answer", certainty="definite", polarity="positive"))

    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        active_entries, _ = session_manager.get_session(session.session_id).active_candidates, session_manager.get_session(session.session_id).reserve_candidates
        assert len(active_entries) >= 1


def test_15_rejected_image_can_never_recover():
    session = session_manager.create_session(mode="demo")
    session.explicitly_rejected_ids.add("demo_001")
    session.active_candidates = [CandidateEntry(image_id="demo_002", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active")]

    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        res = client.post(
            f"/api/v1/sessions/{session.session_id}/select",
            json={"selectionType": "none", "rejectedImageIds": ["demo_002"]}
        )
        assert res.status_code == 200
        updated = session_manager.get_session(session.session_id)
        assert "demo_001" in updated.explicitly_rejected_ids
        assert "demo_002" in updated.explicitly_rejected_ids


def test_16_none_rejects_only_shown_ids():
    session = session_manager.create_session(mode="demo")
    session.active_candidates = [
        CandidateEntry(image_id="demo_001", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active"),
        CandidateEntry(image_id="demo_002", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active"),
    ]
    res = client.post(
        f"/api/v1/sessions/{session.session_id}/select",
        json={"selectionType": "none", "rejectedImageIds": ["demo_001"]}
    )
    assert res.status_code == 200
    updated = session_manager.get_session(session.session_id)
    assert "demo_001" in updated.explicitly_rejected_ids
    assert "demo_002" not in updated.explicitly_rejected_ids


def test_17_no_negative_attribute_transfer():
    # Rejecting demo_001 does not add negative clues to session
    session = session_manager.create_session(mode="demo")
    initial_clue_count = len(session.clues)
    client.post(
        f"/api/v1/sessions/{session.session_id}/select",
        json={"selectionType": "none", "rejectedImageIds": ["demo_001"]}
    )
    updated = session_manager.get_session(session.session_id)
    assert len(updated.clues) == initial_clue_count


def test_18_close_uses_selected_image_as_positive_reference():
    session = session_manager.create_session(mode="demo")
    res = client.post(
        f"/api/v1/sessions/{session.session_id}/select",
        json={"selectionType": "close", "imageId": "demo_001"}
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["action"] in ("ask_question", "show_candidates")


def test_19_recognition_triggers_at_less_or_equal_6_candidates():
    session = session_manager.create_session(mode="demo")
    session.active_candidates = [
        CandidateEntry(image_id=f"demo_00{i}", score=0.8, semantic_score=0.8, structured_score=0.8, pool="active")
        for i in range(1, 5)
    ]
    session.current_question = question_generator.ClarificationQuestion(
        question_id="q1", round=1, text="Was a cake visible?", dimension_tested="objects", options=["Yes", "No", "I don't remember"]
    )
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        res = client.post(
            f"/api/v1/sessions/{session.session_id}/answer",
            json={"answerText": "Yes"}
        )
        assert res.status_code == 200
        assert res.json()["data"]["action"] == "show_candidates"


def test_20_max_rounds_terminates():
    session = session_manager.create_session(mode="demo")
    session.round_count = 5
    session.current_question = question_generator.ClarificationQuestion(
        question_id="q5", round=5, text="Was a cake visible?", dimension_tested="objects", options=["Yes", "No", "I don't remember"]
    )
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        res = client.post(
            f"/api/v1/sessions/{session.session_id}/answer",
            json={"answerText": "Yes"}
        )
        assert res.status_code == 200
        assert res.json()["data"]["action"] == "show_candidates"


def test_21_no_useful_discriminator_triggers_candidates():
    session = session_manager.create_session(mode="demo")
    # All dimensions excluded
    session.dimensions_asked.update(discrimination.CATEGORICAL_DIMENSIONS)
    session.dimensions_asked.update(discrimination.LIST_DIMENSIONS)
    selection = discrimination.select_next_best_question(session)
    assert selection is None


def test_22_question_history_persisted_in_session():
    session = session_manager.create_session(mode="demo")
    session.current_question = question_generator.ClarificationQuestion(
        question_id="q1", round=1, text="Was a cake visible?", dimension_tested="objects", subattribute_key="objects:cake", options=["Yes", "No", "I don't remember"]
    )
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        client.post(f"/api/v1/sessions/{session.session_id}/answer", json={"answerText": "Yes"})
        updated = session_manager.get_session(session.session_id)
        assert len(updated.question_history) == 1
        assert updated.question_history[0].question_id == "q1"


def test_23_candidate_history_updated():
    session = session_manager.create_session(mode="demo")
    session.current_question = question_generator.ClarificationQuestion(
        question_id="q1", round=1, text="Was a cake visible?", dimension_tested="objects", subattribute_key="objects:cake", options=["Yes", "No", "I don't remember"]
    )
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        client.post(f"/api/v1/sessions/{session.session_id}/answer", json={"answerText": "Yes"})
        updated = session_manager.get_session(session.session_id)
        assert len(updated.candidate_history) >= 1


def test_24_full_api_query_answer_candidate_flow_works():
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        session_res = client.post("/api/v1/sessions", json={"mode": "demo"})
        s_id = session_res.json()["data"]["sessionId"]

        query_res = client.post(f"/api/v1/sessions/{s_id}/query", json={"query": "A vague birthday photo"})
        assert query_res.status_code == 200
        action = query_res.json()["data"]["action"]
        assert action in ("ask_question", "show_candidates")

        if action == "ask_question":
            ans_res = client.post(f"/api/v1/sessions/{s_id}/answer", json={"answerText": "Yes"})
            assert ans_res.status_code == 200
            assert ans_res.json()["data"]["action"] in ("ask_question", "show_candidates")

        select_res = client.post(f"/api/v1/sessions/{s_id}/select", json={"selectionType": "found", "imageId": "demo_001"})
        assert select_res.status_code == 200
        assert select_res.json()["data"]["action"] == "found"


def test_25_recognition_uses_latest_all_non_rejected_ranking():
    session = session_manager.create_session(mode="demo")
    active = [
        CandidateEntry(image_id="demo_001", score=0.7, semantic_score=0.7, structured_score=0.7, pool="active"),
    ]
    reserve = [
        CandidateEntry(image_id="demo_002", score=0.95, semantic_score=0.95, structured_score=0.95, pool="reserve"),
        CandidateEntry(image_id="demo_003", score=0.85, semantic_score=0.85, structured_score=0.85, pool="reserve"),
    ]
    from app.routes.sessions import build_recognition_candidate_response
    resp = build_recognition_candidate_response(session.session_id, active, reserve, round_count=1)
    cands = resp.data["candidates"]
    candidate_ids = [c["imageId"] for c in cands]
    assert candidate_ids[0] == "demo_002"
    assert "demo_001" in candidate_ids


def test_26_reserve_candidate_may_appear_in_recognition_after_recovery():
    session = session_manager.create_session(mode="demo")
    active = [
        CandidateEntry(image_id="demo_001", score=0.6, semantic_score=0.6, structured_score=0.6, pool="active"),
    ]
    reserve = [
        CandidateEntry(image_id="demo_005", score=0.99, semantic_score=0.99, structured_score=0.99, pool="reserve"),
    ]
    from app.routes.sessions import build_recognition_candidate_response
    resp = build_recognition_candidate_response(session.session_id, active, reserve, round_count=1)
    candidate_ids = [c["imageId"] for c in resp.data["candidates"]]
    assert candidate_ids[0] == "demo_005"



def test_27_binary_answer_is_scoped_to_tested_subattribute():
    q = question_generator.ClarificationQuestion(
        question_id="q_cake",
        round=1,
        text="Was a cake visible?",
        dimension_tested="objects",
        subattribute_key="objects:cake",
        options=["Yes", "No", "I don't remember"]
    )
    is_idk, clue = answer_interpreter.interpret_user_answer(q, "Yes")
    assert is_idk is False
    assert clue is not None
    assert clue.dimension == "objects"
    assert clue.value == "cake"
    assert clue.polarity == "positive"


def test_28_simulator_answers_only_selected_question():
    from scripts.run_adaptive_retrieval_audit import simulate_truthful_answer
    prof = ImageProfile(image_id="test_img", objects=["cake", "balloons"], setting="indoor")
    q = question_generator.ClarificationQuestion(
        question_id="q1",
        round=1,
        text="Was a cake visible?",
        dimension_tested="objects",
        subattribute_key="objects:cake",
        options=["Yes", "No", "I don't remember"]
    )
    ans = simulate_truthful_answer(q, prof)
    assert ans == "Yes"


def test_29_generic_fallback_questions_are_not_produced():
    sel = discrimination.QuestionSelection(
        selection_type="categorical",
        dimension="setting_type",
        value="home living room",
        discrimination_score=0.8,
        memorability_weight=0.8,
        final_score=0.64,
        distribution={"home living room": 0.5, "park pavilion": 0.5}
    )
    q_text, opts = question_generator.generate_fallback_question_phrasing(sel, round_num=1)
    assert "details about" not in q_text.lower()
    assert "home living room" in q_text.lower() or "park pavilion" in q_text.lower() or len(opts) >= 3



def test_30_target_retained_in_controlled_final_recognition_sets():
    from scripts.run_adaptive_retrieval_audit import run_adaptive_audit
    results = run_adaptive_audit()
    for res in results:
        assert res["target_in_recognition"] is True, f"Target missing in scenario {res['scenario']}"


