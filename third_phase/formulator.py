import json
import re
from typing import Optional, List, Dict, Any
from agents.llm_client import LLMClient
from third_phase.models import (
    FormulationOutput,
    ResearchHypothesis,
    ArchitecturalBlueprint,
    PipelineStage,
    ExperimentProtocol,
)

SYSTEM_PROMPT = """You are a Principal AI & Systems Research Scientist.
Your goal is to formulate novel, mathematically and experimentally sound research hypotheses, design a next-generation methodological framework, and establish a rigorous experimental validation protocol based on synthesized literature and identified research gaps."""

FORMULATION_PROMPT_TEMPLATE = """Based on the literature synthesis for the topic: "{topic}", formulate novel hypotheses and a proposed architectural framework.

IDENTIFIED GAPS:
{gaps_text}

REVIEWED LITERATURE:
{papers_text}

Generate a comprehensive proposal as a valid JSON object matching the following structure:
{{
  "hypotheses": [
    {{
      "id": "H1",
      "statement": "Clear, falsifiable hypothesis statement",
      "rationale": "Theoretical grounding based on reviewed literature",
      "targeted_gaps": ["Gap title addressed"],
      "expected_impact": "Expected outcome"
    }}
  ],
  "proposed_framework": {{
    "framework_name": "Novel Framework Name (e.g. Adaptive-SenseNet)",
    "overview": "High-level summary of the architectural innovation",
    "pipeline_stages": [
      {{
        "stage_name": "Stage 1",
        "function": "Purpose of stage",
        "recommended_technique": "Algorithm or architecture to use"
      }}
    ],
    "key_innovations": [
      "Innovation 1...",
      "Innovation 2..."
    ]
  }},
  "experimental_protocol": {{
    "recommended_datasets": ["Dataset / testbed 1", "Dataset 2"],
    "baseline_models_to_compare": ["Baseline 1", "Baseline 2"],
    "evaluation_metrics": ["Metric 1 (e.g. Accuracy, F1)", "Metric 2 (e.g. Latency)"],
    "ablation_studies": ["Ablation test 1", "Ablation test 2"]
  }}
}}

Respond ONLY with the JSON object.
"""


def formulate_research_directions(
    topic: str,
    phase1_papers: List[Dict[str, Any]],
    phase2_synthesis: Dict[str, Any],
    llm_client: Optional[LLMClient] = None
) -> FormulationOutput:
    """
    Formulate hypotheses, architectural blueprint, and experiment protocol.
    Uses LLM with heuristic fallback.
    """
    if llm_client is None:
        llm_client = LLMClient()

    # Format gaps & top chapter foundations from Phase 2
    gaps = phase2_synthesis.get("identified_research_gaps", [])
    top_reads = phase2_synthesis.get("top_recommended_reading", [])
    
    gaps_lines = [f"- [{g.get('impact_level', 'High')}] {g.get('gap_title')}: {g.get('description')}" for g in gaps]
    if top_reads:
        gaps_lines.append("\nTOP CHAPTER FOUNDATIONS (PHASE 2 RANKING):")
        for r in top_reads:
            gaps_lines.append(f"- Best {r.get('chapter_type')}: '{r.get('best_paper')}' ({r.get('score')})")

    gaps_text = "\n".join(gaps_lines) or "Cross-environment adaptation and real-time inference latency challenges."

    # Format papers
    papers_text = "\n".join(
        f"- {p.get('paper', {}).get('title')} ({p.get('paper', {}).get('year', 'N/A')}): {p.get('core_problem', '')[:100]}"
        for p in phase1_papers[:4]
    )

    prompt = FORMULATION_PROMPT_TEMPLATE.format(
        topic=topic,
        gaps_text=gaps_text,
        papers_text=papers_text
    )

    try:
        raw_response = llm_client.complete(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=3000,
            response_json=True
        )
        parsed = _parse_json(raw_response)
        if parsed:
            hypotheses = [ResearchHypothesis(**h) for h in parsed.get("hypotheses", [])]
            fw = parsed.get("proposed_framework", {})
            stages = [PipelineStage(**s) for s in fw.get("pipeline_stages", [])]
            framework = ArchitecturalBlueprint(
                framework_name=fw.get("framework_name", f"Adaptive {topic} Framework"),
                overview=fw.get("overview", "A modular deep sensing framework"),
                pipeline_stages=stages,
                key_innovations=fw.get("key_innovations", [])
            )
            proto = parsed.get("experimental_protocol", {})
            protocol = ExperimentProtocol(
                recommended_datasets=proto.get("recommended_datasets", []),
                baseline_models_to_compare=proto.get("baseline_models_to_compare", []),
                evaluation_metrics=proto.get("evaluation_metrics", []),
                ablation_studies=proto.get("ablation_studies", [])
            )
            return FormulationOutput(
                topic=topic,
                hypotheses=hypotheses,
                proposed_framework=framework,
                experimental_protocol=protocol
            )
    except Exception as e:
        print(f"[Formulator] LLM formulation unavailable ({e}). Using heuristic formulation.")

    return _heuristic_formulate(topic, gaps)


def _parse_json(raw: str) -> Optional[dict]:
    clean = raw.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\n?", "", clean)
        clean = re.sub(r"\n?```$", "", clean)
    try:
        return json.loads(clean)
    except Exception:
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
    return None


def _heuristic_formulate(topic: str, gaps: List[Dict[str, Any]]) -> FormulationOutput:
    """Heuristic generation of hypotheses and framework when LLM is unavailable."""
    h1 = ResearchHypothesis(
        id="H1",
        statement=f"Incorporating self-supervised contrastive pretraining on raw spatial signatures will boost cross-environment adaptation accuracy in {topic} by at least 15% without retraining.",
        rationale="Supervised models suffer severe domain drift across rooms/environments; self-supervised representations learn environment-invariant spatial dynamics.",
        targeted_gaps=["Cross-Domain and Environmental Generalization"],
        expected_impact="Eliminates the cumbersome recalibration phase typically required for deployment in new physical locations."
    )

    h2 = ResearchHypothesis(
        id="H2",
        statement=f"A dual-stream spatial-temporal neural network that decouples static background multipath from dynamic movement will reduce inference latency by >40% on edge devices.",
        rationale="Static environmental reflections consume redundant compute; isolating dynamic Doppler shifts enables lightweight temporal convolutions.",
        targeted_gaps=["Real-Time Computational Efficiency on Edge Hardware"],
        expected_impact="Enables continuous, low-power real-time sensing on micro-controller / commodity edge hardware."
    )

    stages = [
        PipelineStage(
            stage_name="Stage 1: Phase Sanitization & Multipath Removal",
            function="Clean raw RF/channel state information and calibrate phase shifts.",
            recommended_technique="Linear phase unwrapping and high-pass Butterworth Doppler filter."
        ),
        PipelineStage(
            stage_name="Stage 2: Environment-Invariant Representation",
            function="Extract invariant spatial features across varying physical configurations.",
            recommended_technique="Self-supervised contrastive encoder with temporal augmentations."
        ),
        PipelineStage(
            stage_name="Stage 3: Spatio-Temporal Movement Classification",
            function="Detect and classify fine-grained movement, gestures, or trajectory tracking.",
            recommended_technique="Lightweight Temporal Convolutional Network (TCN) with multi-head attention."
        )
    ]

    framework = ArchitecturalBlueprint(
        framework_name=f"RobustSense-{re.sub(r'[^a-zA-Z0-9]', '', topic.title())}",
        overview=f"An end-to-end domain-adaptive pipeline for {topic} designed to handle multipath interference and minimize calibration overhead.",
        pipeline_stages=stages,
        key_innovations=[
            "Dynamic/static multipath decoupling module.",
            "Environment-invariant contrastive embedding space.",
            "Lightweight edge-deployable attention architecture."
        ]
    )

    protocol = ExperimentProtocol(
        recommended_datasets=["SenseFi Benchmark Suite", "Widar 3.0", "Custom Multi-Room Testbed"],
        baseline_models_to_compare=["Standard ResNet-18 Baseline", "Vanilla LSTM / GRU", "Random Forest / SVM Handcrafted"],
        evaluation_metrics=["Macro F1-Score", "Cross-Domain Transfer Accuracy (%)", "Inference Latency (ms)", "Memory Footprint (MB)"],
        ablation_studies=[
            "Impact of self-supervised pretraining vs. direct supervised training.",
            "Performance sensitivity across transmitter-receiver distance variations.",
            "Evaluation with varying numbers of concurrent occupants (interference test)."
        ]
    )

    return FormulationOutput(
        topic=topic,
        hypotheses=[h1, h2],
        proposed_framework=framework,
        experimental_protocol=protocol
    )
