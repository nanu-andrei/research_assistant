---
name: paper_search_and_extraction
description: Searches academic papers across arXiv and Semantic Scholar for a given topic and extracts key ideas, methodologies, contributions, and reference citation networks.
version: 1.0.0
phase: first_phase
---

# Skill: Paper Search and Idea/Reference Extraction (Phase 1)

## Overview
This skill acts as the literature discovery and extraction engine for the research agent. Given a user-defined research topic, it queries academic repositories, de-duplicates results, fetches citations and reference graphs, and extracts core ideas and research questions.

## Capabilities
1. **Multi-Source Academic Search**:
   - **arXiv**: Fetches preprints, titles, abstracts, author rosters, published dates, and PDF links.
   - **Semantic Scholar**: Fetches peer-reviewed papers, citation counts, open-access PDFs, and structured reference lists.
2. **Citation & Reference Resolution**:
   - Enriches arXiv papers with Semantic Scholar reference graphs.
   - Aggregates citations across papers to detect foundational/seminal literature in the topic.
3. **Structured Knowledge Extraction**:
   - Uses LLM (via LiteLLM: Gemini, OpenAI, Claude, Ollama) to extract:
     - Core Problem / Research Gap
     - Methodology & Architecture
     - Key Findings & Quantitative Results
     - Core Innovative Ideas
     - Foundational Prior Works
   - Includes graceful heuristic fallback when no LLM key is configured.
4. **Full-Text PDF Inspection (Optional)**:
   - Downloads and reads open-access PDFs to examine sections beyond the abstract.

## Inputs
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `topic` / `query` | `str` | Yes | - | Research subject (e.g. "multi-agent reinforcement learning", "diffusion models") |
| `max_papers` | `int` | No | `5` | Maximum number of papers to analyze |
| `sources` | `List[str]` | No | `["arxiv", "semantic_scholar"]` | Search backends to query |
| `extract_pdf_text` | `bool` | No | `False` | Whether to download and parse PDF text |

## Outputs
Returns a `SkillResult` with `data` containing `SearchAndExtractionOutput`:
- `query`: The executed search query.
- `total_found`: Number of analyzed papers.
- `papers_analyzed`: List of paper analysis objects:
  - `paper`: Metadata (`paper_id`, `title`, `authors`, `year`, `abstract`, `url`, `pdf_url`, `references`)
  - `core_problem`: Formulated problem statement.
  - `methodology`: Formulated technical approach.
  - `key_findings`: List of empirical results.
  - `main_ideas`: List of novel concepts.
  - `key_references_highlighted`: Crucial citations.
- `aggregated_references`: Flat list of all resolved references.
- `top_recurring_references`: Top citations ranked by recurrence across the retrieved sample.

## Usage Example
```python
from agents.agent import ResearchAgent
from first_phase.skill import PaperSearchAndExtractionSkill

agent = ResearchAgent()
agent.register_skill(PaperSearchAndExtractionSkill())

result = agent.run_skill(
    "paper_search_and_extraction",
    topic="Multi-Agent Debate for LLM Reasoning",
    max_papers=3
)

if result.success:
    print(result.data["papers_analyzed"])
```
