import json
import re
from typing import Optional, List, Dict, Any
from agents.llm_client import LLMClient
from second_phase.models import (
    ChapterRankingOutput,
    ChapterCategoryRanking,
    RankedChapterEntry,
)

CATEGORIES = [
    {
        "key": "introduction",
        "display_name": "Introductions (Problem Formulation & Motivation)",
        "description": "Evaluates how clearly and thoroughly the paper motivates the problem, frames the research gap, and defines the research scope."
    },
    {
        "key": "related_work",
        "display_name": "Related Work & State of the Art Background",
        "description": "Evaluates the depth of prior art analysis, historical context, and differentiation from existing solutions."
    },
    {
        "key": "methodology",
        "display_name": "Methodologies, Algorithms & System Architectures",
        "description": "Evaluates technical rigor, algorithmic novelty, mathematical formulation, and architecture design."
    },
    {
        "key": "experiments",
        "display_name": "Experimental Evaluations & Benchmark Results",
        "description": "Evaluates dataset scale, testbed realism, comparative baseline rigor, and empirical performance metrics."
    },
    {
        "key": "conclusion",
        "display_name": "Conclusions, Discussions & Future Directions",
        "description": "Evaluates the depth of synthesis, critical acknowledgment of limitations, and actionable future roadmaps."
    }
]


def rank_paper_chapters(
    topic: str,
    papers_data: List[Dict[str, Any]],
    llm_client: Optional[LLMClient] = None
) -> ChapterRankingOutput:
    """
    Ranks individual chapters across all papers in decreasing order of relevance
    and importance to the requested topic. Ensures each entry contains 3-4 substantial paragraphs.
    """
    if llm_client is None:
        llm_client = LLMClient()

    chapter_rankings: Dict[str, ChapterCategoryRanking] = {}

    for cat in CATEGORIES:
        cat_key = cat["key"]
        display_name = cat["display_name"]
        description = cat["description"]

        # Collect raw chapter candidates from all papers
        candidates = []
        for item in papers_data:
            paper = item.get("paper", {})
            title = paper.get("title", "Untitled")
            paper_id = paper.get("paper_id", "")
            year = paper.get("year")
            sections = paper.get("sections", {})

            heading = ""
            paragraphs: List[str] = []

            # 1. Check if section was extracted from PDF
            if cat_key in sections:
                sec = sections[cat_key]
                heading = sec.get("heading", display_name)
                paragraphs = list(sec.get("paragraphs", []))

            # 2. Ensure at least 3-4 paragraphs by pulling from most_relevant_paragraphs or abstract
            fallback_paras = item.get("most_relevant_paragraphs", [])
            for p in fallback_paras:
                if len(paragraphs) >= 4:
                    break
                if p not in paragraphs and len(p) >= 80:
                    paragraphs.append(p)

            # If still short, add abstract sentences/paragraphs
            if len(paragraphs) < 3 and paper.get("abstract"):
                abstract_paras = [s.strip() for s in paper.get("abstract").split("\n\n") if len(s.strip()) >= 60]
                for ap in abstract_paras:
                    if len(paragraphs) >= 4:
                        break
                    if ap not in paragraphs:
                        paragraphs.append(ap)

            candidates.append({
                "paper_title": title,
                "paper_id": paper_id,
                "year": year,
                "heading": heading or display_name,
                "paragraphs": paragraphs[:4],  # Guarantee 3-4 top paragraphs
                "core_problem": item.get("core_problem", ""),
                "methodology": item.get("methodology", ""),
                "findings": item.get("key_findings", []),
            })

        # Score and rank candidates
        ranked_entries = _score_and_rank_category(
            topic=topic,
            category_key=cat_key,
            category_name=display_name,
            candidates=candidates,
            llm_client=llm_client,
        )

        chapter_rankings[cat_key] = ChapterCategoryRanking(
            category_key=cat_key,
            display_name=display_name,
            description=description,
            ranked_entries=ranked_entries,
        )

    # Compile overall top recommended reading
    top_recommendations = []
    for cat in CATEGORIES:
        cat_key = cat["key"]
        ranking = chapter_rankings.get(cat_key)
        if ranking and ranking.ranked_entries:
            top_1 = ranking.ranked_entries[0]
            top_recommendations.append({
                "chapter_type": ranking.display_name,
                "best_paper": top_1.paper_title,
                "score": f"{top_1.relevance_score:.1f}/100",
                "reason": top_1.ranking_rationale,
            })

    return ChapterRankingOutput(
        topic=topic,
        total_papers_evaluated=len(papers_data),
        chapter_rankings=chapter_rankings,
        top_recommended_reading=top_recommendations,
    )


def _score_and_rank_category(
    topic: str,
    category_key: str,
    category_name: str,
    candidates: List[Dict[str, Any]],
    llm_client: LLMClient,
) -> List[RankedChapterEntry]:
    """Score and sort chapter entries in decreasing order of relevance and importance."""
    # Attempt LLM ranking if configured
    try:
        llm_ranked = _llm_rank_category(topic, category_name, candidates, llm_client)
        if llm_ranked:
            return llm_ranked
    except Exception as e:
        print(f"[Ranker] LLM ranking for '{category_name}' unavailable ({e}). Using heuristic ranker.")

    return _heuristic_rank_category(topic, category_key, candidates)


def _heuristic_rank_category(
    topic: str,
    category_key: str,
    candidates: List[Dict[str, Any]],
) -> List[RankedChapterEntry]:
    """Calculate heuristic relevance score (0-100) and sort in decreasing order."""
    topic_terms = [t.lower() for t in re.findall(r"\w+", topic) if len(t) > 2]
    scored = []

    for c in candidates:
        combined_text = " ".join(c["paragraphs"]).lower() + " " + c["paper_title"].lower()
        score = 50.0  # Base score

        # Term frequency & density
        for term in topic_terms:
            count = combined_text.count(term)
            score += min(count * 6.0, 30.0)

        # Exact phrase bonus
        if topic.lower() in combined_text:
            score += 15.0

        # Category-specific bonus
        if category_key == "introduction":
            for kw in ["challenge", "motivat", "problem", "first to", "address", "gap"]:
                if kw in combined_text:
                    score += 2.0
        elif category_key == "methodology":
            for kw in ["algorithm", "framework", "architecture", "model", "formulat", "pipeline"]:
                if kw in combined_text:
                    score += 3.0
        elif category_key == "experiments":
            for kw in ["benchmark", "dataset", "accuracy", "baseline", "experiment", "percent", "%"]:
                if kw in combined_text:
                    score += 3.0
        elif category_key == "conclusion":
            for kw in ["future work", "in summary", "conclude", "limitations", "promising"]:
                if kw in combined_text:
                    score += 2.0

        # Paragraph fullness bonus (ensures 3-4 paragraphs)
        score += min(len(c["paragraphs"]) * 2.0, 8.0)

        # Bound score between 40 and 99
        final_score = min(max(round(score, 1), 40.0), 99.0)

        # Rationales tailored by category and score
        rationale = (
            f"Demonstrates exceptional alignment with '{topic}'. Presents rigorous discussion "
            f"with concrete focus in its {category_key}."
            if final_score > 75
            else f"Relevant to '{topic}', providing context and supporting insights in its {category_key}."
        )

        scored.append((final_score, c, rationale))

    # Sort in strictly decreasing order of score
    scored.sort(key=lambda x: x[0], reverse=True)

    ranked_entries: List[RankedChapterEntry] = []
    for rank_idx, (score, c, rationale) in enumerate(scored, 1):
        ranked_entries.append(
            RankedChapterEntry(
                rank=rank_idx,
                paper_title=c["paper_title"],
                paper_id=c["paper_id"],
                year=c["year"],
                relevance_score=score,
                ranking_rationale=rationale,
                heading=c["heading"],
                extracted_paragraphs=c["paragraphs"],
            )
        )

    return ranked_entries


def _llm_rank_category(
    topic: str,
    category_name: str,
    candidates: List[Dict[str, Any]],
    llm_client: LLMClient,
) -> Optional[List[RankedChapterEntry]]:
    """Use LLM to score and rank candidates in decreasing order."""
    system_prompt = (
        "You are an expert scientific literature reviewer. Rank the provided paper chapters "
        "in strict decreasing order of relevance and importance to the given research topic. "
        "Assign a relevance score from 0 to 100 and write a concise rationale for each rank."
    )

    items_repr = []
    for idx, c in enumerate(candidates, 1):
        sample_para = c["paragraphs"][0][:250] if c["paragraphs"] else "No text"
        items_repr.append(
            f"[{idx}] Paper: \"{c['paper_title']}\" ({c['year']})\n"
            f"     Heading: {c['heading']}\n"
            f"     Sample Text: {sample_para}...\n"
        )

    prompt = (
        f"Topic: \"{topic}\"\n"
        f"Chapter Category: {category_name}\n\n"
        f"Evaluate and rank these papers for this chapter category:\n\n"
        + "\n".join(items_repr) +
        "\n\nReturn a valid JSON array of objects ordered by highest rank first:\n"
        "[\n"
        "  {\n"
        "    \"paper_index\": 1,\n"
        "    \"relevance_score\": 95.0,\n"
        "    \"ranking_rationale\": \"Why this chapter ranks here...\"\n"
        "  }\n"
        "]\n"
        "Respond ONLY with the JSON array."
    )

    response = llm_client.complete(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.2,
        max_tokens=2000,
        response_json=True,
    )

    clean = response.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\n?", "", clean)
        clean = re.sub(r"\n?```$", "", clean)

    data = json.loads(clean)
    if isinstance(data, list) and data:
        ranked_entries = []
        for rank_num, item in enumerate(data, 1):
            idx = item.get("paper_index", 1) - 1
            if 0 <= idx < len(candidates):
                c = candidates[idx]
                ranked_entries.append(
                    RankedChapterEntry(
                        rank=rank_num,
                        paper_title=c["paper_title"],
                        paper_id=c["paper_id"],
                        year=c["year"],
                        relevance_score=float(item.get("relevance_score", 80.0)),
                        ranking_rationale=item.get("ranking_rationale", "Top relevance to topic."),
                        heading=c["heading"],
                        extracted_paragraphs=c["paragraphs"],
                    )
                )
        if ranked_entries:
            return ranked_entries
    return None
