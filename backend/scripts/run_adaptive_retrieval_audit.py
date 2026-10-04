from __future__ import annotations
import os
import sys
import json
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.services import (
    session_manager,
    query_parser,
    embedding_service,
    image_understanding_service,
    candidate_retriever,
    discrimination,
    question_generator,
    answer_interpreter,
    gemini_client,
)
from scripts.generate_demo_embeddings import generate_deterministic_synthetic_vector

logging.basicConfig(level=logging.ERROR)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "data"))
HARD_SCENARIOS_PATH = os.path.join(DATA_DIR, "hard_retrieval_scenarios.json")


def simulate_truthful_answer(question, target_profile) -> str:
    """
    Simulates a truthful user answer derived strictly from the target ImageProfile.
    """
    dim = question.dimension_tested
    subkey = question.subattribute_key
    val_focus = selection_meta_value(question)

    if subkey or ":" in dim:
        v_name = subkey.split(":")[1] if subkey and ":" in subkey else val_focus
        items = getattr(target_profile, dim, []) or []
        present = any(v_name in str(it).lower() for it in items)
        return "Yes" if present else "No"

    # Categorical
    if dim == "setting":
        return "Indoors" if target_profile.setting == "indoor" else "Outdoors"
    elif dim == "people_count":
        cnt = target_profile.people_count or "3+"
        if cnt == "1":
            return "Solo (1 person)"
        elif cnt == "2":
            return "2 people"
        else:
            return "Group (3+ people)"
    elif dim == "occasion":
        occ = target_profile.occasion or ""
        if "birthday" in occ.lower():
            return "Birthday"
        elif "wedding" in occ.lower():
            return "Wedding"
        elif "festival" in occ.lower():
            return "Festival"
        elif "vacation" in occ.lower():
            return "Vacation"
        elif "picnic" in occ.lower():
            return "Picnic"
        else:
            return "Casual"
    elif dim == "activity":
        act = target_profile.activity or ""
        if "celebrat" in act.lower():
            return "Celebrating"
        elif "eat" in act.lower() or "picnic" in act.lower():
            return "Eating / Picnic"
        elif "play" in act.lower() or "sport" in act.lower():
            return "Playing / Sports"
        elif "walk" in act.lower() or "travel" in act.lower():
            return "Walking / Travel"
        else:
            return "Posing"
    elif dim == "time_of_day":
        tod = target_profile.time_of_day or ""
        if tod == "golden_hour":
            return "Sunset / Golden hour"
        elif tod == "night":
            return "Night"
        else:
            return "Daytime"

    # Default
    return "Yes"


def selection_meta_value(question) -> str:
    if question.selection_metadata and question.selection_metadata.value:
        return question.selection_metadata.value
    return ""


def run_adaptive_audit():
    with open(HARD_SCENARIOS_PATH, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    results = []

    for sc in scenarios:
        sc_id = sc["scenario_id"]
        init_query = sc["query"]
        target_id = sc["target_image_id"]

        session = session_manager.create_session(mode="demo")
        session.original_query = init_query

        # 1. Parse initial query clues
        init_clues = query_parser.parse_query_to_clues(init_query)
        for clue in init_clues:
            session_manager.add_clue(session.session_id, clue)
            session.dimensions_provided_by_user.add(clue.dimension)

        # 2. Get embeddings & profiles
        embeddings_map = embedding_service.get_session_embeddings(session.session_id)
        profiles_list = image_understanding_service.get_session_profiles(session.session_id)
        profiles_map = {p.image_id: p for p in profiles_list}
        target_prof = profiles_map[target_id]

        has_api_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key")
        query_vec = None
        if has_api_key:
            try:
                query_vec = gemini_client.embed_text(init_query)
            except Exception:
                pass

        if not query_vec:
            query_vec = generate_deterministic_synthetic_vector(init_query)

        # 3. Initial Baseline Ranking
        initial_ranked = candidate_retriever.rank_candidates_composite(
            query_embedding=query_vec,
            image_embeddings=embeddings_map,
            image_profiles=profiles_map,
            clues=session.clues,
        )

        init_rank = None
        for idx, (img_id, score, sem, struct) in enumerate(initial_ranked, start=1):
            if img_id == target_id:
                init_rank = idx
                break

        # Set initial candidate pools (top 12 active, rest reserve)
        active_limit = getattr(settings, "INITIAL_ACTIVE_LIMIT", 12)
        active_entries = []
        reserve_entries = []
        for rank_idx, (img_id, final_score, sem_score, struct_score) in enumerate(initial_ranked, start=1):
            is_active = (rank_idx <= active_limit)
            entry = candidate_retriever.CandidateEntry(
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

        session_manager.set_candidate_pools(session.session_id, active_entries, reserve_entries)

        questions_asked = []
        rounds_history = []
        rounds_history.append((0, len(active_entries), len(reserve_entries)))

        # 4. Adaptive Questioning Loop
        for round_idx in range(1, 6):
            selection = discrimination.select_next_best_question(session)
            if not selection or len(session.active_candidates) <= 6:
                break

            question = question_generator.generate_clarification_question(selection, round_idx)
            session.current_question = question
            session.round_count = round_idx

            # Simulate truthful answer from target
            answer_text = simulate_truthful_answer(question, target_prof)
            questions_asked.append(f"{question.subattribute_key or question.dimension_tested} ('{answer_text}')")

            # Interpret & rescore
            is_idk, clue = answer_interpreter.interpret_user_answer(question, answer_text)
            session.dimensions_asked.add(question.dimension_tested)
            if question.subattribute_key:
                session.subattributes_asked.add(question.subattribute_key)

            if clue:
                session.clues.append(clue)

            # Rescore ALL candidates
            new_ranked = candidate_retriever.rank_candidates_composite(
                query_embedding=query_vec,
                image_embeddings=embeddings_map,
                image_profiles=profiles_map,
                clues=session.clues,
            )

            new_active = []
            new_reserve = []
            for r_idx, (img_id, final_score, sem_score, struct_score) in enumerate(new_ranked, start=1):
                is_act = (r_idx <= active_limit)
                e = candidate_retriever.CandidateEntry(
                    image_id=img_id,
                    score=round(final_score, 4),
                    semantic_score=round(sem_score, 4),
                    structured_score=round(struct_score, 4),
                    pool="active" if is_act else "reserve",
                    profile=profiles_map[img_id].model_dump() if img_id in profiles_map else None,
                )
                if is_act:
                    new_active.append(e)
                else:
                    new_reserve.append(e)

            session_manager.set_candidate_pools(session.session_id, new_active, new_reserve)
            rounds_history.append((round_idx, len(new_active), len(new_reserve)))

        # Final Recognition Candidate Set (Top 6 from latest complete non-rejected ranking)
        final_ranked = candidate_retriever.rank_candidates_composite(
            query_embedding=query_vec,
            image_embeddings=embeddings_map,
            image_profiles=profiles_map,
            clues=session.clues,
        )

        recognition_ids = [img_id for (img_id, _, _, _) in final_ranked[:6]]

        final_rank = None
        for idx, (img_id, score, sem, struct) in enumerate(final_ranked, start=1):
            if img_id == target_id:
                final_rank = idx
                break

        target_in_rec = (target_id in recognition_ids)
        count_path = " -> ".join([str(h[1]) for h in rounds_history])

        results.append({
            "scenario": sc_id,
            "query": init_query,
            "target": target_id,
            "initial_rank": init_rank,
            "final_rank": final_rank,
            "final_rec_count": len(recognition_ids),
            "target_in_recognition": target_in_rec,
            "questions": questions_asked,
            "count_path": count_path,
        })

    print("=== PHASE 6 ADAPTIVE RETRIEVAL AUDIT RESULTS ===")
    print(f"{'Scenario':<8} | {'Target':<9} | {'Init Rank':<9} | {'Questions Asked':<17} | {'Final Rank':<10} | {'Rec Count':<9} | {'Target in Rec?':<14} | {'Count Path'}")
    print("-" * 110)
    for r in results:
        q_cnt = str(len(r["questions"]))
        retained_str = "YES" if r["target_in_recognition"] else "NO"
        print(f"{r['scenario']:<8} | {r['target']:<9} | #{r['initial_rank']:<8} | {q_cnt:<17} | #{r['final_rank']:<9} | {r['final_rec_count']:<9} | {retained_str:<14} | {r['count_path']}")

    # Assert that target is retained in recognition set for all hard scenarios
    failed_scenarios = [r["scenario"] for r in results if not r["target_in_recognition"]]
    if failed_scenarios:
        print(f"\nERROR: Target was NOT retained in recognition set for scenarios: {failed_scenarios}")
    else:
        print("\nSUCCESS: Target photo was retained in final recognition set for ALL 5 hard scenarios!")

    return results


if __name__ == "__main__":
    run_adaptive_audit()
