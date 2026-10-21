from typing import Dict, Any, Optional
from rich.console import Console

from agents.base_skill import BaseSkill, SkillResult
from agents.llm_client import LLMClient
from second_phase.ranker import rank_paper_chapters

console = Console()


class ChapterRankingSkill(BaseSkill):
    """
    Phase 2 Skill: Chapter-Level Relevance & Importance Ranking.
    Ranks individual chapters (Introduction, Related Work, Methodology,
    Experiments, Conclusion) across all papers in decreasing order of relevance
    to the requested research topic. Extracts 3-4 deep paragraphs per chapter.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        super().__init__(
            name="chapter_ranking_and_synthesis",
            description="Ranks major chapters (Introduction, Methodology, Experiments, etc.) across all papers in decreasing order of relevance, extracting 3-4 rich paragraphs per chapter.",
        )
        self.llm_client = llm_client or LLMClient()

    def execute(self, context: Dict[str, Any], **kwargs) -> SkillResult:
        phase1_data = context.get("paper_search_and_extraction", {})
        papers = phase1_data.get("papers_analyzed", [])
        topic = kwargs.get("topic") or context.get("topic") or phase1_data.get("query", "Academic Topic")

        if not papers:
            return SkillResult(
                success=False,
                error="No analyzed papers found in agent context. Run 'paper_search_and_extraction' first.",
            )

        console.print(f"  [bold]Ranking chapters across {len(papers)} papers for topic:[/bold] '{topic}'")
        console.print("  [cyan]* Evaluating Introductions, Methodologies, Experiments, Related Work, and Conclusions in decreasing order...[/cyan]")

        ranking_output = rank_paper_chapters(
            topic=topic,
            papers_data=papers,
            llm_client=self.llm_client,
        )

        # Store also under legacy key so downstream third phase continues seamlessly
        context["literature_synthesis"] = ranking_output.model_dump()

        summary = (
            f"Successfully ranked {len(ranking_output.chapter_rankings)} major chapter categories "
            f"across {ranking_output.total_papers_evaluated} papers in decreasing order of relevance. "
            f"Extracted 3-4 deep paragraphs per chapter."
        )

        return SkillResult(
            success=True,
            data=ranking_output.model_dump(),
            summary=summary,
        )


# Backward compatibility alias
LiteratureSynthesisSkill = ChapterRankingSkill
