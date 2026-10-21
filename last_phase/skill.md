---
name: latex_paper_compiler
description: Assembles modular chapters written in IEEE format, generates BibTeX citations, and compiles the final paper into a camera-ready PDF using Tectonic.
version: 1.0.0
phase: last_phase
---

# Skill: IEEE LaTeX Paper Assembly & Compilation (Last Phase)

## Overview
This skill acts as the final publication layer of the agent pipeline. It collects the individual chapter files produced by the specialized chapter-writing skills (`IntroductionWriterSkill`, `RelatedWorkWriterSkill`, `MethodologyWriterSkill`, `ExperimentsWriterSkill`, `ConclusionWriterSkill`), generates a BibTeX citation database, constructs the master `main.tex` adhering to the IEEE conference format (`IEEEtran.cls`), and compiles the document into a publication-ready PDF using **Tectonic**.

## Inputs
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `context["final_paper_chapters"]` | `dict` | Yes | Individual LaTeX chapters generated in Phase 3 |
| `context["paper_search_and_extraction"]` | `dict` | Yes | Paper metadata used for BibTeX entries |
| `topic` | `str` | No | Title research subject |
| `paper_dir` | `str` | No | Target output directory (default: `outputs/paper`) |

## Outputs
- `outputs/paper/main.tex`: Master IEEE LaTeX document.
- `outputs/paper/sections/*.tex`: Modular chapter files.
- `outputs/paper/references.bib`: Generated BibTeX database.
- `outputs/paper/paper.pdf`: Camera-ready compiled IEEE 2-column research paper PDF.
