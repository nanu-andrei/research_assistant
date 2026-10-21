from third_phase.writing_skills import (
    IntroductionWriterSkill,
    RelatedWorkWriterSkill,
    MethodologyWriterSkill,
    ExperimentsWriterSkill,
    ConclusionWriterSkill,
)
from third_phase.formulator import formulate_research_directions
from third_phase.models import (
    FormulationOutput,
    ResearchHypothesis,
    ArchitecturalBlueprint,
    PipelineStage,
    ExperimentProtocol,
)
from agents.base_skill import BaseSkill, SkillResult
from agents.llm_client import LLMClient
from rich.console import Console

console = Console()


class ResearchFormulationSkill(BaseSkill):
    """
    Phase 3 Skill: Research Hypothesis & Methodology / Experiment Formulation.
    """

    def __init__(self, llm_client=None):
        super().__init__(
            name="research_formulation",
            description="Formulates testable hypotheses, architectural blueprints, and experimental validation protocols based on literature gaps.",
        )
        self.llm_client = llm_client or LLMClient()

    def execute(self, context, **kwargs):
        phase1_data = context.get("paper_search_and_extraction", {})
        phase2_data = context.get("chapter_ranking_and_synthesis", {}) or context.get("literature_synthesis", {})

        papers = phase1_data.get("papers_analyzed", [])
        topic = kwargs.get("topic") or context.get("topic") or phase1_data.get("query", "Academic Topic")

        console.print(f"  [bold]Formulating Research Directions for:[/bold] '{topic}'")
        output = formulate_research_directions(
            topic=topic,
            phase1_papers=papers,
            phase2_synthesis=phase2_data,
            llm_client=self.llm_client,
        )

        return SkillResult(
            success=True,
            data=output.model_dump(),
            summary=f"Formulated {len(output.hypotheses)} hypotheses and '{output.proposed_framework.framework_name}' architecture.",
        )


__all__ = [
    "IntroductionWriterSkill",
    "RelatedWorkWriterSkill",
    "MethodologyWriterSkill",
    "ExperimentsWriterSkill",
    "ConclusionWriterSkill",
    "ResearchFormulationSkill",
    "FormulationOutput",
    "ResearchHypothesis",
    "ArchitecturalBlueprint",
    "PipelineStage",
    "ExperimentProtocol",
]
