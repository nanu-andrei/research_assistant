import json
import re
from typing import Optional, List
from agents.llm_client import LLMClient
from first_phase.models import PaperMetadata, ExtractedPaperAnalysis

SYSTEM_PROMPT = """You are an expert academic research assistant specializing in deep literature review, concept extraction, and citation network analysis.
Your job is to analyze the provided academic paper details (title, abstract, text) and extract the core ideas, methodology, findings, and references in a clean, structured JSON format."""

ANALYSIS_PROMPT_TEMPLATE = """Analyze the following academic paper:

TITLE: {title}
AUTHORS: {authors}
YEAR: {year}
ABSTRACT:
{abstract}

ADDITIONAL CONTEXT / TEXT:
{context}

Please extract and return a valid JSON object with the following fields:
{{
  "core_problem": "Precise summary of the problem, gap, or research question addressed",
  "methodology": "The technical approach, architecture, algorithm, dataset, or mathematical formulation used",
  "key_findings": ["List of 2-4 major concrete results or performance outcomes"],
  "main_ideas": ["List of 2-4 core innovative concepts, principles, or theoretical takeaways"],
  "key_references_highlighted": ["List of 2-4 key foundational citations or prior works referenced"],
  "limitations": "Any stated limitations, assumptions, or future work (or 'Not explicitly stated' if none)"
}}

Respond ONLY with the JSON object. Do not wrap in markdown tags if possible, or use standard ```json.
"""


def extract_paper_analysis(
    paper: PaperMetadata,
    llm_client: Optional[LLMClient] = None,
    additional_text: str = ""
) -> ExtractedPaperAnalysis:
    """
    Extract structured ideas, methodology, and findings from paper metadata and text.
    Uses LLM when available; falls back to rule-based heuristics if LLM is unavailable or unconfigured.
    """
    if llm_client is None:
        llm_client = LLMClient()

    # If there's an LLM available, try calling it
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        title=paper.title,
        authors=", ".join(paper.authors),
        year=paper.year or "Unknown",
        abstract=paper.abstract or "No abstract provided",
        context=additional_text[:3000] if additional_text else "None"
    )

    try:
        raw_response = llm_client.complete(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.2,
            max_tokens=1500,
            response_json=True
        )
        data = _parse_llm_json(raw_response)
        if data:
            return ExtractedPaperAnalysis(
                paper=paper,
                core_problem=data.get("core_problem", ""),
                methodology=data.get("methodology", ""),
                key_findings=data.get("key_findings", []),
                main_ideas=data.get("main_ideas", []),
                key_references_highlighted=data.get("key_references_highlighted", []),
                limitations=data.get("limitations")
            )
    except Exception as e:
        print(f"[Extractor] LLM extraction encountered error ({e}). Using heuristic extraction.")

    # Fallback to heuristic extraction
    return _heuristic_extract(paper)


def _parse_llm_json(raw: str) -> Optional[dict]:
    """Parse JSON safely from LLM output."""
    clean = raw.strip()
    # Strip markdown fences if present
    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\n?", "", clean)
        clean = re.sub(r"\n?```$", "", clean)
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None


def _heuristic_extract(paper: PaperMetadata) -> ExtractedPaperAnalysis:
    """Rule-based heuristic extraction from abstract when LLM is unavailable."""
    abstract = paper.abstract or ""
    sentences = [s.strip() for s in re.split(r"[.!?]\s+", abstract) if len(s.strip()) > 10]

    core_problem = sentences[0] if sentences else f"Investigation into {paper.title}"
    methodology = sentences[1] if len(sentences) > 1 else "Methodology detailed in full text."
    
    findings = []
    if len(sentences) > 2:
        findings.extend(sentences[2:min(len(sentences), 5)])
    else:
        findings.append(abstract[:150] + "..." if abstract else "See abstract for details.")

    main_ideas = [
        f"Contributions in the domain of '{paper.title}'",
        f"Approach by {', '.join(paper.authors[:2]) if paper.authors else 'the authors'}"
    ]

    ref_titles = [r.title for r in paper.references[:5] if r.title]

    return ExtractedPaperAnalysis(
        paper=paper,
        core_problem=core_problem,
        methodology=methodology,
        key_findings=findings,
        main_ideas=main_ideas,
        key_references_highlighted=ref_titles,
        limitations="Heuristic mode: Configure LLM_MODEL & API key for in-depth reasoning."
    )
