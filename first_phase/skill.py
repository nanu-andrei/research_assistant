import re
from collections import Counter
from typing import Dict, Any, List, Optional
from rich.console import Console

from agents.base_skill import BaseSkill, SkillResult
from agents.llm_client import LLMClient
from first_phase.models import (
    PaperMetadata,
    PaperReference,
    ExtractedPaperAnalysis,
    SearchAndExtractionOutput,
)
from first_phase.arxiv_search import search_arxiv
from first_phase.semantic_scholar_search import (
    search_semantic_scholar,
    fetch_references_for_paper,
)
from first_phase.pdf_reader import download_and_extract_pdf_text
from first_phase.extractor import extract_paper_analysis

console = Console()


def _normalize_title(title: str) -> str:
    """Normalize paper title for fuzzy de-duplication."""
    return re.sub(r"[^a-zA-Z0-9]", "", title.lower())


class PaperSearchAndExtractionSkill(BaseSkill):
    """
    Skill for Phase 1:
    - Searches academic papers across arXiv and Semantic Scholar.
    - Resolves and enriches citation references.
    - Extracts key ideas, methodologies, and contributions using LLM.
    - Aggregates the most recurring foundational references.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        super().__init__(
            name="paper_search_and_extraction",
            description="Searches academic papers on a given topic, extracts key ideas, contributions, and reference networks.",
        )
        self.llm_client = llm_client or LLMClient()

    def execute(self, context: Dict[str, Any], **kwargs) -> SkillResult:
        query = kwargs.get("topic") or kwargs.get("query") or context.get("topic") or context.get("query")
        if not query:
            return SkillResult(
                success=False,
                error="No research 'topic' or 'query' provided in arguments or agent context.",
            )

        max_papers = kwargs.get("max_papers", context.get("max_papers", 5))
        sources = kwargs.get("sources", context.get("sources", ["arxiv", "semantic_scholar"]))
        extract_pdf_text = kwargs.get("extract_pdf_text", False)

        console.print(f"  [bold]Research Topic:[/bold] '{query}'")
        console.print(f"  [bold]Target Sources:[/bold] {sources}")
        console.print(f"  [bold]Max Papers:[/bold] {max_papers}")

        all_papers: List[PaperMetadata] = []

        # 1. Search Semantic Scholar
        if "semantic_scholar" in sources:
            console.print("  [cyan]• Querying Semantic Scholar API...[/cyan]")
            s2_papers = search_semantic_scholar(query, max_results=max_papers)
            console.print(f"    Found {len(s2_papers)} papers on Semantic Scholar.")
            all_papers.extend(s2_papers)

        # 2. Search arXiv
        if "arxiv" in sources:
            console.print("  [cyan]• Querying arXiv API...[/cyan]")
            arxiv_papers = search_arxiv(query, max_results=max_papers)
            console.print(f"    Found {len(arxiv_papers)} papers on arXiv.")
            all_papers.extend(arxiv_papers)

        if not all_papers:
            return SkillResult(
                success=False,
                error=f"No papers found for topic: '{query}'. Try a broader query or alternative terms.",
            )

        # 3. De-duplicate papers
        deduped_papers: List[PaperMetadata] = []
        seen_titles = set()
        for p in all_papers:
            norm = _normalize_title(p.title)
            if norm and norm not in seen_titles:
                seen_titles.add(norm)
                deduped_papers.append(p)

        # Limit to max_papers
        selected_papers = deduped_papers[:max_papers]
        console.print(f"  [bold green]Selected {len(selected_papers)} unique papers for deep extraction.[/bold green]")

        # 4. Enrich references and extract ideas
        analyzed_papers: List[ExtractedPaperAnalysis] = []
        all_references: List[PaperReference] = []

        for idx, paper in enumerate(selected_papers, 1):
            console.print(f"\n  [yellow]({idx}/{len(selected_papers)}) Analyzing:[/yellow] [italic]{paper.title[:75]}...[/italic]")

            # If paper is from arXiv and has no references, attempt Semantic Scholar resolution
            if not paper.references and paper.paper_id.startswith("arxiv:"):
                arxiv_clean_id = paper.paper_id.replace("arxiv:", "")
                console.print(f"    Enriching references for arXiv ID: {arxiv_clean_id}")
                fetched_refs = fetch_references_for_paper(f"ARXIV:{arxiv_clean_id}")
                if fetched_refs:
                    paper.references = fetched_refs
                    console.print(f"    Retrieved {len(fetched_refs)} references from citation graph.")

            # Optional PDF text download
            pdf_context = ""
            if extract_pdf_text and paper.pdf_url:
                console.print(f"    Extracting text from PDF: {paper.pdf_url}")
                pdf_context = download_and_extract_pdf_text(paper.pdf_url, max_pages=5)

            # Analyze paper ideas using LLM
            analysis = extract_paper_analysis(
                paper=paper,
                llm_client=self.llm_client,
                additional_text=pdf_context
            )
            analyzed_papers.append(analysis)

            # Collect references
            if paper.references:
                all_references.extend(paper.references)

        # 5. Aggregate top recurring references across retrieved papers
        ref_counter = Counter(
            f"{r.title} ({r.year})" if r.year else r.title
            for r in all_references
            if r.title and len(r.title) > 5
        )
        top_refs = [
            {"reference": ref, "citation_frequency_in_sample": count}
            for ref, count in ref_counter.most_common(10)
        ]

        output = SearchAndExtractionOutput(
            query=query,
            total_found=len(analyzed_papers),
            papers_analyzed=analyzed_papers,
            aggregated_references=all_references,
            top_recurring_references=top_refs,
        )

        summary = (
            f"Extracted ideas from {len(analyzed_papers)} papers. "
            f"Aggregated {len(all_references)} citations with {len(top_refs)} top recurring foundational references."
        )

        return SkillResult(
            success=True,
            data=output.model_dump(),
            summary=summary,
        )
