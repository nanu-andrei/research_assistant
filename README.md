# Multi-Skill Academic Research Agent

An extensible, modular agent pipeline designed for academic literature discovery, knowledge extraction, and reference synthesis across structured phases.

## Project Architecture

```
Slaves/
│── .env.example               # Template for API keys & model configuration
│── requirements.txt           # Python dependencies
│── main.py                    # Main agent execution CLI
│
├── agents/                    # Core Agent System
│   ├── base_skill.py          # BaseSkill interface & SkillResult definition
│   ├── llm_client.py          # Provider-agnostic LLM interface (Gemini, OpenAI, Claude, Ollama)
│   └── agent.py               # ResearchAgent coordinator & shared context manager
│
├── first_phase/               # Phase 1: Search & Knowledge/Reference Extraction
│   ├── skill.md               # Detailed skill specification & documentation
│   ├── skill.py               # PaperSearchAndExtractionSkill implementation
│   ├── models.py              # Pydantic data schemas
│   ├── arxiv_search.py        # arXiv search & Atom XML parser
│   ├── semantic_scholar_search.py # Semantic Scholar Graph API client & reference resolver
│   ├── pdf_reader.py          # PDF text & reference extractor
│   └── extractor.py           # Structured idea & problem extraction (LLM + heuristic fallback)
│
├── second_phase/              # Phase 2: Literature Synthesis & Gap Analysis (Upcoming)
│   └── skill.md               # Phase 2 Blueprint & specification
│
├── third_phase/               # Phase 3: Hypothesis & Experiment Formulation (Upcoming)
│   └── skill.md               # Phase 3 Blueprint & specification
│
└── last_phase/                # Phase 4: Final Survey Report & LaTeX/BibTeX Export (Upcoming)
    └── skill.md               # Final Phase Blueprint & specification
```

---

## Getting Started

### 1. Environment Setup
Activate the virtual environment:
```powershell
.\.venv\Scripts\Activate.ps1
```

Dependencies are installed via `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### 2. Configure LLM (Optional / Flexible)
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Edit `.env` to set your desired model and key (supports Google Gemini, OpenAI, Anthropic, or Ollama):
```env
LLM_MODEL=gemini/gemini-2.0-flash
GEMINI_API_KEY=your_key_here
```
> **Note:** If no API key is provided, the agent runs in **Heuristic Fallback Mode**, extracting structured sentences and bibliographic data without error!

---

## Running the Agent

### Basic Usage
Run the agent CLI by passing a research topic:
```powershell
.\.venv\Scripts\python.exe main.py --topic "Multi-Agent Systems for LLM Reasoning"
```

Or interactively prompt:
```powershell
.\.venv\Scripts\python.exe main.py
```

### Options & Flags
- `--topic`, `-t`: Subject or research topic to search for.
- `--max-papers`, `-m`: Number of papers to retrieve and analyze (default: `3`).
- `--sources`, `-s`: Repositories to search (`arxiv`, `semantic_scholar`).
- `--extract-pdf`: Download and parse open-access PDF contents.
- `--output-dir`, `-o`: Directory where output files are stored (default: `outputs`).

### Output Artifacts
Each run automatically generates:
1. `outputs/{topic}_analysis.json`: Full machine-readable structured JSON containing extracted problems, methodologies, findings, and reference lists.
2. `outputs/{topic}_report.md`: Markdown summary report with tables and citation recurrence frequencies.

---

## Adding New Skills (Phases 2, 3, Last Phase)

To add a new skill to the agent:
1. Define the skill specification in `{phase}/skill.md`.
2. Inherit from `BaseSkill` in `{phase}/skill.py`:
   ```python
   from agents.base_skill import BaseSkill, SkillResult

   class LiteratureSynthesisSkill(BaseSkill):
       def __init__(self):
           super().__init__(name="literature_synthesis", description="Synthesizes gaps across papers")

       def execute(self, context: dict, **kwargs) -> SkillResult:
           # Access outputs from previous phase:
           phase1_data = context.get("paper_search_and_extraction")
           # ... perform synthesis ...
           return SkillResult(success=True, data={"synthesis": "..."})
   ```
3. Register the skill with the agent:
   ```python
   agent.register_skill(LiteratureSynthesisSkill())
   ```
