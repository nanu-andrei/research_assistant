---
name: research_formulation
description: Formulates testable research hypotheses, designs novel architectural frameworks, and establishes experimental protocols based on synthesized literature and identified gaps.
version: 1.0.0
phase: third_phase
---

# Skill: Research Hypothesis & Methodology Formulation (Phase 3)

## Overview
This skill acts as the creative and methodological formulation layer of the agent pipeline. It translates the gaps and comparative synthesis generated in Phase 2 (`literature_synthesis`) into concrete, actionable scientific directions:
1. **Testable Hypotheses**: Formulated with clear theoretical rationale and expected measurable outcomes.
2. **Architectural Blueprint**: End-to-end algorithmic or system architecture specifying pipeline stages and technical components.
3. **Experimental Validation Protocol**: Rigorous testing methodology including benchmark datasets, baseline comparative models, evaluation metrics, and ablation studies.

## Inputs
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `context["paper_search_and_extraction"]` | `dict` | Yes | Analyzed literature from Phase 1 |
| `context["literature_synthesis"]` | `dict` | Yes | Comparative matrix and gaps from Phase 2 |
| `topic` | `str` | No | Overriding research topic name |

## Outputs
Returns a `SkillResult` with `data` containing `FormulationOutput`:
- `topic`: Topic name.
- `hypotheses`: List of `ResearchHypothesis` objects (id, statement, rationale, targeted gaps, expected impact).
- `proposed_framework`: `ArchitecturalBlueprint` object (framework name, overview, pipeline stages, innovations).
- `experimental_protocol`: `ExperimentProtocol` object (datasets, baselines, evaluation metrics, ablation studies).

## Usage Example
```python
from agents.agent import ResearchAgent
from first_phase.skill import PaperSearchAndExtractionSkill
from second_phase.skill import LiteratureSynthesisSkill
from third_phase.skill import ResearchFormulationSkill

agent = ResearchAgent()
agent.register_skill(PaperSearchAndExtractionSkill())
agent.register_skill(LiteratureSynthesisSkill())
agent.register_skill(ResearchFormulationSkill())

# Execute full 3-phase pipeline
context = agent.run_pipeline(
    initial_context={"topic": "WiFi Movement Detection", "max_papers": 3}
)
```
