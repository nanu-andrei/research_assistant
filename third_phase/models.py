from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ResearchHypothesis(BaseModel):
    """Testable scientific hypothesis addressing identified research gaps."""
    id: str = "H1"
    statement: str
    rationale: str
    targeted_gaps: List[str] = Field(default_factory=list)
    expected_impact: str


class PipelineStage(BaseModel):
    """Stage in the proposed methodological pipeline."""
    stage_name: str
    function: str
    recommended_technique: str


class ArchitecturalBlueprint(BaseModel):
    """Proposed novel system architecture or methodological framework."""
    framework_name: str
    overview: str
    pipeline_stages: List[PipelineStage] = Field(default_factory=list)
    key_innovations: List[str] = Field(default_factory=list)


class ExperimentProtocol(BaseModel):
    """Experimental validation protocol to test the hypotheses."""
    recommended_datasets: List[str] = Field(default_factory=list)
    baseline_models_to_compare: List[str] = Field(default_factory=list)
    evaluation_metrics: List[str] = Field(default_factory=list)
    ablation_studies: List[str] = Field(default_factory=list)


class FormulationOutput(BaseModel):
    """Output container for Phase 3 Research Formulation."""
    topic: str
    hypotheses: List[ResearchHypothesis] = Field(default_factory=list)
    proposed_framework: ArchitecturalBlueprint
    experimental_protocol: ExperimentProtocol
