from __future__ import annotations
import io
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.models.image import ImageProfile
from app.models.clue import Clue
from app.services import (
    session_manager,
    search_document,
    candidate_retriever,
    query_parser,
    embedding_service,
    image_understanding_service,
    upload_service,
)
from scripts.generate_demo_embeddings import generate_deterministic_synthetic_vector

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_test_sessions():
    yield
    session_manager.clear_all_sessions()


def test_1_deterministic_search_document_generation():
    prof = ImageProfile(
        image_id="img_1",
        setting="indoor",
        activity="celebrating",
        occasion="birthday",
        clothing=["pink dress"],
        objects=["cake", "balloons"],
        dominant_colors=["pink", "white"],
        free_description="Childhood birthday party indoors.",
        identity_tags=["Sister"],
    )

    doc1 = search_document.build_search_document(prof)
    doc2 = search_document.build_search_document(prof)
    assert doc1 == doc2
    assert "Setting: indoor." in doc1
    assert "Activity: celebrating." in doc1
    assert "Known identities: Sister." in doc1


def test_2_and_3_identity_tags_manual_only():
    prof_manual = ImageProfile(
        image_id="img_m",
        setting="outdoor",
        identity_tags=["Mom", "Dad"],
    )
    doc_manual = search_document.build_search_document(prof_manual)
    assert "Known identities: Mom, Dad." in doc_manual

    # Ensure raw dict from AI cannot inject identity tags if manually empty
    prof_auto = image_understanding_service.build_and_validate_image_profile(
        image_id="img_a",
        raw_dict={"setting": "outdoor", "identity_tags": ["FakeIdentity"]},
        identity_tags=[],
    )
    assert prof_auto.identity_tags == []
    doc_auto = search_document.build_search_document(prof_auto)
    assert "Known identities" not in doc_auto


def test_4_and_5_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]

    sim_identical = candidate_retriever.cosine_similarity(v1, v2)
    sim_orthogonal = candidate_retriever.cosine_similarity(v1, v3)

    assert pytest.approx(sim_identical, 0.001) == 1.0
    assert pytest.approx(sim_orthogonal, 0.001) == 0.0
    assert sim_identical > sim_orthogonal


def test_6_candidate_ranking_sorts_correctly():
    query_vec = [1.0, 0.0]
    embs = {
        "c1": [0.9, 0.1],
        "c2": [0.1, 0.9],
        "c3": [1.0, 0.0],
    }
    profs = {
        "c1": ImageProfile(image_id="c1", setting="indoor"),
        "c2": ImageProfile(image_id="c2", setting="indoor"),
        "c3": ImageProfile(image_id="c3", setting="indoor"),
    }
    ranked = candidate_retriever.rank_candidates_composite(query_vec, embs, profs, [])
    assert ranked[0][0] == "c3"
    assert ranked[1][0] == "c1"
    assert ranked[2][0] == "c2"


def test_7_and_8_clue_certainty_weights():
    prof = ImageProfile(image_id="c1", setting="indoor")

    clue_definite = Clue(dimension="setting", value="indoor", source="user_initial", certainty="definite")
    clue_unsure = Clue(dimension="setting", value="indoor", source="user_initial", certainty="unsure")
    clue_inferred = Clue(dimension="setting", value="indoor", source="inferred", certainty="inferred")

    score_def = candidate_retriever.compute_structured_clue_agreement(prof, [clue_definite])
    score_unsure = candidate_retriever.compute_structured_clue_agreement(prof, [clue_unsure])
    score_inf = candidate_retriever.compute_structured_clue_agreement(prof, [clue_inferred])

    assert score_def > score_unsure > score_inf


def test_9_and_10_initial_retrieval_pool_population():
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        session = session_manager.create_session(mode="demo")
        res = client.post(
            f"/api/v1/sessions/{session.session_id}/query",
            json={"query": "That birthday party with something pink"},
        )
        assert res.status_code == 200
        data = res.json()["data"]

        updated_session = session_manager.get_session(session.session_id)
        assert len(updated_session.active_candidates) > 0
        assert len(updated_session.explicitly_rejected_ids) == 0
        assert updated_session.retrieval_status == "in_progress"


def test_11_target_retained_in_active_set():
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        session = session_manager.create_session(mode="demo")
        res = client.post(
            f"/api/v1/sessions/{session.session_id}/query",
            json={"query": "Childhood birthday party indoors with a pink dress and cake"},
        )
        assert res.status_code == 200
        updated_session = session_manager.get_session(session.session_id)
        image_ids = [c.image_id for c in updated_session.active_candidates]
        assert "demo_001" in image_ids


def test_12_13_14_query_updates_session_state():
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        session = session_manager.create_session(mode="demo")
        res = client.post(
            f"/api/v1/sessions/{session.session_id}/query",
            json={"query": "I think I was wearing pink indoors"},
        )
        assert res.status_code == 200

        updated_session = session_manager.get_session(session.session_id)
        assert updated_session.original_query == "I think I was wearing pink indoors"
        assert "setting" in updated_session.dimensions_provided_by_user or len(updated_session.clues) > 0

        assert len(updated_session.candidate_history) == 1
        h_entry = updated_session.candidate_history[0]
        assert h_entry.round == 0
        assert h_entry.trigger == "initial_retrieval"
        assert h_entry.rejected_count == 0


def test_15_invalid_empty_query_rejected():
    session = session_manager.create_session(mode="demo")
    res = client.post(
        f"/api/v1/sessions/{session.session_id}/query",
        json={"query": "   "},
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "EMPTY_QUERY"


def test_16_research_session_without_photos_rejected():
    session = session_manager.create_session(mode="research")
    res = client.post(
        f"/api/v1/sessions/{session.session_id}/query",
        json={"query": "My beach photo"},
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "LIBRARY_EMPTY"


def test_17_18_research_embeddings_session_isolation_and_cleanup():
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        s1 = session_manager.create_session(mode="research")
        s2 = session_manager.create_session(mode="research")

        fake_img = io.BytesIO(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00")
        client.post(
            f"/api/v1/sessions/{s1.session_id}/upload",
            files=[("files", ("res1.jpg", fake_img, "image/jpeg"))],
        )

        embs1 = embedding_service.get_session_embeddings(s1.session_id)
        embs2 = embedding_service.get_session_embeddings(s2.session_id)

        assert len(embs1) == 1
        assert len(embs2) == 0

        # Session 2 cannot retrieve Session 1 embeddings
        img_id_1 = list(embs1.keys())[0]
        assert img_id_1 not in embs2

        # Cleanup Session 1
        session_manager.delete_session(s1.session_id)
        assert len(embedding_service.get_session_embeddings(s1.session_id)) == 0


def test_19_demo_embeddings_load_without_provider():
    embeddings = embedding_service.load_demo_embeddings()
    assert isinstance(embeddings, dict)
    assert "demo_001" in embeddings
    assert len(embeddings["demo_001"]) > 0
