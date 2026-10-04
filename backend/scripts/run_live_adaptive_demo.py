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

logging.basicConfig(level=logging.INFO)


def run_live_demo():
    print("=== LIVE END-TO-END ADAPTIVE BACKEND DEMO ===")
    vague_query = "That birthday picture from years ago where there were decorations"
    target_id = "demo_002"  # Target: Birthday party with yellow decorations and cake

    print(f"1. Initial Vague Query: \"{vague_query}\"")
    print(f"   Target Photo: {target_id}")

    session = session_manager.create_session(mode="demo")
    session.original_query = vague_query

    # Parse initial clues
    clues = query_parser.parse_query_to_clues(vague_query)
    for clue in clues:
        session_manager.add_clue(session.session_id, clue)
        session.dimensions_provided_by_user.add(clue.dimension)

    embeddings_map = embedding_service.get_session_embeddings(session.session_id)
    profiles_list = image_understanding_service.get_session_profiles(session.session_id)
    profiles_map = {p.image_id: p for p in profiles_list}

    # Embed query
    query_vec = gemini_client.embed_text(vague_query)

    # Initial Ranking
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

    print(f"\n2. Initial Retrieval Result:")
    print(f"   Total Library Candidates: {len(initial_ranked)}")
    print(f"   Initial Target Rank: #{init_rank}")

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

    # Question Selection 1
    selection1 = discrimination.select_next_best_question(session)
    if selection1:
        print("\n3. Question 1 Selected by Discrimination Engine:")
        print(f"   - Selected Dimension: {selection1.dimension}")
        print(f"   - Subattribute Key: {selection1.subattribute_key or 'N/A'}")
        print(f"   - Value Focus: {selection1.value}")
        print(f"   - WHY Numerically:")
        print(f"       * Discrimination Score: {selection1.discrimination_score}")
        print(f"       * Memorability Weight:  {selection1.memorability_weight}")
        print(f"       * Final Question Score: {selection1.final_score}")
        print(f"       * Candidate Distribution: {selection1.distribution}")

        q1 = question_generator.generate_clarification_question(selection1, round_num=1)
        session.current_question = q1
        print(f"   - Phrased Question: \"{q1.text}\"")
        print(f"   - Options Provided: {q1.options}")

        from scripts.run_adaptive_retrieval_audit import simulate_truthful_answer

        # Answer question 1 truthfully based on target profile
        answer1 = simulate_truthful_answer(q1, profiles_map[target_id])
        print(f"\n4. User Answer (Truthful to Question 1): \"{answer1}\"")

        is_idk, clue1 = answer_interpreter.interpret_user_answer(q1, answer1)
        session.dimensions_asked.add(q1.dimension_tested)
        if q1.subattribute_key:
            session.subattributes_asked.add(q1.subattribute_key)
        if clue1:
            session.clues.append(clue1)

        # Rescore ALL candidates
        new_ranked = candidate_retriever.rank_candidates_composite(
            query_embedding=query_vec,
            image_embeddings=embeddings_map,
            image_profiles=profiles_map,
            clues=session.clues,
        )

        new_rank = None
        for idx, (img_id, score, sem, struct) in enumerate(new_ranked, start=1):
            if img_id == target_id:
                new_rank = idx
                break

        print(f"\n5. Candidate Rank & Count Change After Answer 1:")
        print(f"   - Target Rank After Answer 1: #{new_rank} (was #{init_rank})")
        print(f"   - Top Candidate: {new_ranked[0][0]} (score: {new_ranked[0][1]:.4f})")

        # Question Selection 2
        selection2 = discrimination.select_next_best_question(session)
        if selection2:
            print("\n6. Question 2 Selected by Discrimination Engine:")
            print(f"   - Selected Dimension: {selection2.dimension}")
            print(f"   - Subattribute Key: {selection2.subattribute_key or 'N/A'}")
            print(f"   - Final Question Score: {selection2.final_score}")

            q2 = question_generator.generate_clarification_question(selection2, round_num=2)
            print(f"   - Phrased Question: \"{q2.text}\"")

            answer2 = simulate_truthful_answer(q2, profiles_map[target_id])
            print(f"   - User Answer (Truthful to Question 2): \"{answer2}\"")

            is_idk2, clue2 = answer_interpreter.interpret_user_answer(q2, answer2)
            session.dimensions_asked.add(q2.dimension_tested)
            if q2.subattribute_key:
                session.subattributes_asked.add(q2.subattribute_key)
            if clue2:
                session.clues.append(clue2)

            new_ranked = candidate_retriever.rank_candidates_composite(
                query_embedding=query_vec,
                image_embeddings=embeddings_map,
                image_profiles=profiles_map,
                clues=session.clues,
            )

    # Final Recognition Candidate Set (Top 6 from latest global non-rejected ranking)
    recognition_set = new_ranked[:6]
    recognition_ids = [img_id for (img_id, _, _, _) in recognition_set]
    target_visible = (target_id in recognition_ids)

    print("\n7. Recognition Candidate Set Returned to User:")
    for idx, (img_id, score, sem, struct) in enumerate(recognition_set, start=1):
        is_t = " <-- TARGET IDENTIFIED" if img_id == target_id else ""
        print(f"   Rank #{idx}: {img_id:<10} | Score: {score:.4f} {is_t}")

    print(f"\nTarget Final Rank: #{new_ranked.index(next(r for r in new_ranked if r[0] == target_id)) + 1}")
    print(f"Target Visible in Recognition Set: {target_visible}")


if __name__ == "__main__":
    run_live_demo()
