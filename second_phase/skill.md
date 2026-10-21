---
name: chapter_ranking_and_synthesis
description: Ranks individual chapters (Introduction, Methodology, Experiments, Related Work, Conclusion) across all reviewed papers in decreasing order of relevance and importance to the topic, extracting at least 3-4 deep paragraphs per chapter.
version: 2.0.0
phase: second_phase
---

# Skill: Chapter-Level Relevance & Importance Ranking (Phase 2)

## Overview
This skill implements fine-grained chapter/section evaluation across all academic papers discovered in Phase 1. Instead of generic summaries, it systematically evaluates and ranks specific sections:
1. **Introductions** (Problem formulation, motivation, research scope)
2. **Related Work / Background** (State of the art, differentiation)
3. **Methodologies & System Architectures** (Technical formulation, algorithms)
4. **Experimental Evaluations & Results** (Datasets, accuracy, empirical rigor)
5. **Conclusions & Future Directions** (Synthesis, limitations, roadmap)

For each major chapter category, all candidate papers are ranked in **decreasing order of relevance and importance** to the requested topic.

## Depth Requirement (3-4 Paragraphs)
To provide actionable research value beyond one-liners, each ranked chapter entry extracts **at least 3-4 substantial paragraphs** that have the highest relevance to the requested topic.

## Outputs
Returns a `SkillResult` with `data` containing `ChapterRankingOutput`:
- `topic`: Research domain.
- `total_papers_evaluated`: Count of papers analyzed.
- `chapter_rankings`: Dictionary keyed by chapter category (`introduction`, `methodology`, etc.) containing:
  - `display_name`: Category title.
  - `ranked_entries`: List of entries ordered by Rank 1, Rank 2, Rank 3...:
    - `rank`: Rank number (1 is best).
    - `paper_title`: Paper title.
    - `relevance_score`: Quantitative relevance score (0-100).
    - `ranking_rationale`: Scientific justification for the rank.
    - `heading`: Section heading in the paper.
    - `extracted_paragraphs`: 3-4 rich paragraphs extracted from the chapter.
- `top_recommended_reading`: Executive list of which paper has the single best Introduction, best Methodology, best Experiment setup, etc.
