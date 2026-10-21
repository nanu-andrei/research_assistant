# Multi-Skill Academic Research Agent

An extensible, modular agent pipeline designed for academic literature discovery, knowledge synthesis, and hypothesis formulation across structured phases.

## Project Architecture

```
Slaves/
│── .env.example                         # Template for API keys & model configuration
│── requirements.txt                     # Python dependencies
│── main.py                              # Main agent execution CLI
│
├── agents/                              # Core Agent System
│   ├── base_skill.py                    # BaseSkill interface & SkillResult definition
│   ├── llm_client.py                    # Provider-agnostic LLM interface (Gemini, OpenAI, Claude, Ollama)
│   └── agent.py                         # ResearchAgent coordinator & shared context manager
│
├── first_phase/                         # Phase 1: Search & Knowledge/Reference Extraction
│   ├── skill.md                         # Detailed Phase 1 specification
│   ├── skill.py                         # PaperSearchAndExtractionSkill implementation
│   ├── models.py                        # Pydantic data schemas
│   ├── arxiv_search.py                  # arXiv search & Atom XML parser
│   ├── semantic_scholar_search.py       # Semantic Scholar Graph API client & reference resolver
│   ├── pdf_reader.py                    # PDF text & reference extractor
│   └── extractor.py                     # Structured idea & problem extraction
│
├── second_phase/                        # Phase 2: Literature Synthesis & Gap Analysis
│   ├── skill.md                         # Detailed Phase 2 specification
│   ├── skill.py                         # LiteratureSynthesisSkill implementation
│   ├── models.py                        # SynthesisOutput & ResearchGap schemas
│   └── synthesizer.py                   # Comparative matrix & gap detection engine
│
├── third_phase/                         # Phase 3: Hypothesis Formulation & System Blueprint
│   ├── skill.md                         # Detailed Phase 3 specification
│   ├── skill.py                         # ResearchFormulationSkill implementation
│   ├── models.py                        # FormulationOutput & ArchitecturalBlueprint schemas
│   └── formulator.py                    # Hypothesis & experimental protocol generator
│
└── last_phase/                          # Phase 4: Final Survey Report & LaTeX/BibTeX Export (Upcoming)
    └── skill.md                         # Final Phase Blueprint
```

---

## Running the Agent

### Run All 3 Phases
Run the complete pipeline from paper discovery through gap analysis to hypothesis & architecture formulation:
```powershell
.\.venv\Scripts\python.exe main.py --topic "wifi movement detection" --max-papers 3
```

### Run Specific Phases
You can also run specific phases using `--phases`:
```powershell
# Run only Phase 1 (search & reference extraction)
.\.venv\Scripts\python.exe main.py --topic "wifi movement detection" --phases 1

# Run Phase 1 and Phase 2 (search + comparative synthesis)
.\.venv\Scripts\python.exe main.py --topic "wifi movement detection" --phases 1 2

# Run all 3 phases
.\.venv\Scripts\python.exe main.py --topic "wifi movement detection" --phases 1 2 3
```

### Output Dossier
Outputs are saved in `outputs/`:
- `outputs/{topic}_full_research.md`: Full multi-phase research document (Literature review, Comparative matrix, Gaps, Hypotheses, Proposed Architecture, and Experimental Protocol).
- `outputs/{topic}_full_research.json`: Complete serialized pipeline context.
