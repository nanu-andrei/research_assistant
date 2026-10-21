import os
import sys
import json
import argparse
import re
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from agents.agent import ResearchAgent
from first_phase.skill import PaperSearchAndExtractionSkill
from second_phase.skill import ChapterRankingSkill, LiteratureSynthesisSkill
from third_phase.skill import (
    IntroductionWriterSkill,
    RelatedWorkWriterSkill,
    MethodologyWriterSkill,
    ExperimentsWriterSkill,
    ConclusionWriterSkill,
    ResearchFormulationSkill,
)
from last_phase.skill import LatexPaperCompilerSkill

console = Console()


def slugify(text: str) -> str:
    """Generate safe filename slug from text."""
    slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", slug)[:50]


def save_comprehensive_report(output_dir: Path, topic: str, context: dict):
    """Save full multi-phase research report as JSON and Markdown."""
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(topic)

    json_path = output_dir / f"{slug}_full_research.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2, ensure_ascii=False)

    md_path = output_dir / f"{slug}_full_research.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Comprehensive Academic Research Dossier: {topic}\n\n")

        # ---------------- Phase 1 ----------------
        p1 = context.get("paper_search_and_extraction", {})
        if p1:
            f.write("## Phase 1: Literature Discovery & Reference Extraction\n\n")
            f.write(f"- **Total Papers Analyzed:** {p1.get('total_found', 0)}\n")
            f.write(f"- **Total References Aggregated:** {len(p1.get('aggregated_references', []))}\n\n")

            for idx, item in enumerate(p1.get("papers_analyzed", []), 1):
                p = item.get("paper", {})
                f.write(f"### 1.{idx} {p.get('title')}\n")
                f.write(f"- **Authors:** {', '.join(p.get('authors', []))}\n")
                f.write(f"- **Year:** {p.get('year') or 'N/A'}\n")
                if p.get("url"):
                    f.write(f"- **URL:** [{p.get('url')}]({p.get('url')})\n")
                if p.get("pdf_url"):
                    f.write(f"- **PDF:** [{p.get('pdf_url')}]({p.get('pdf_url')})\n")
                if p.get("local_pdf_path"):
                    f.write(f"- **Local Downloaded PDF:** `{p.get('local_pdf_path')}`\n")
                f.write(f"- **Source:** `{p.get('source')}`\n\n")

                f.write(f"**Core Problem / Gap:**\n> {item.get('core_problem')}\n\n")
                f.write(f"**Methodology / Approach:**\n> {item.get('methodology')}\n\n")

                f.write("**Key Findings:**\n")
                for finding in item.get("key_findings", []):
                    f.write(f"- {finding}\n")
                f.write("\n")

                f.write("**Main Ideas & Contributions:**\n")
                for idea in item.get("main_ideas", []):
                    f.write(f"- {idea}\n")
                f.write("\n")

                if item.get("key_references_highlighted"):
                    f.write("**Key Prior Works Highlighted:**\n")
                    for ref in item.get("key_references_highlighted", []):
                        f.write(f"- {ref}\n")
                    f.write("\n")
                f.write("---\n\n")

            top_refs = p1.get("top_recurring_references", [])
            if top_refs:
                f.write("### Most Influential / Recurring References in Sample\n\n")
                f.write("| Reference Title | Occurrences Across Retrieved Papers |\n")
                f.write("|---|---|\n")
                for r in top_refs:
                    f.write(f"| {r.get('reference')} | {r.get('citation_frequency_in_sample')} |\n")
                f.write("\n---\n\n")

        # ---------------- Phase 2 ----------------
        p2 = context.get("chapter_ranking_and_synthesis") or context.get("literature_synthesis", {})
        if p2:
            f.write("## Phase 2: Chapter-Level Relevance & Importance Ranking\n\n")

            top_reads = p2.get("top_recommended_reading", [])
            if top_reads:
                f.write("### 2.1 Executive Overview: Best Chapters Across All Papers\n\n")
                f.write("| Major Chapter Category | Best Paper (#1) | Relevance Score | Selection Rationale |\n")
                f.write("|---|---|---|---|\n")
                for r in top_reads:
                    f.write(f"| {r.get('chapter_type')} | **{r.get('best_paper')}** | `{r.get('score')}` | {r.get('reason')} |\n")
                f.write("\n---\n\n")

            rankings = p2.get("chapter_rankings", {})
            if rankings:
                f.write("### 2.2 Detailed Rankings by Chapter (Decreasing Order of Relevance)\n\n")
                for cat_key, cat_data in rankings.items():
                    f.write(f"#### {cat_data.get('display_name')}\n")
                    f.write(f"*{cat_data.get('description')}*\n\n")

                    entries = cat_data.get("ranked_entries", [])
                    for entry in entries:
                        f.write(f"##### Rank {entry.get('rank')}: {entry.get('paper_title')} ({entry.get('year') or 'N/A'})\n")
                        f.write(f"- **Relevance & Importance Score:** `{entry.get('relevance_score'):.1f}/100`\n")
                        if entry.get("heading"):
                            f.write(f"- **Section Heading:** *{entry.get('heading')}*\n")
                        f.write(f"- **Ranking Rationale:** {entry.get('ranking_rationale')}\n\n")

                        paras = entry.get("extracted_paragraphs", [])
                        if paras:
                            f.write(f"**Extracted Relevant Paragraphs ({len(paras)} paragraphs):**\n\n")
                            for p_idx, p_text in enumerate(paras, 1):
                                f.write(f"> **¶{p_idx}.** {p_text}\n\n")
                        f.write("---\n\n")

        # ---------------- Phase 4: Compiled LaTeX Paper ----------------
        compiled_pdf = context.get("final_compiled_pdf")
        if compiled_pdf:
            f.write("## Phase 4: Final Camera-Ready IEEE Research Paper\n\n")
            f.write(f"- **Compiled IEEE PDF Document:** [`{Path(compiled_pdf).name}`]({compiled_pdf})\n")
            f.write(f"- **LaTeX Source File:** [`outputs/paper/main.tex`](file:///C:/Users/Biggus%20Dickus/Desktop/Faculta/master/Slaves/outputs/paper/main.tex)\n")
            f.write(f"- **BibTeX Citations:** [`outputs/paper/references.bib`](file:///C:/Users/Biggus%20Dickus/Desktop/Faculta/master/Slaves/outputs/paper/references.bib)\n\n")

    return json_path, md_path


def display_phase1_in_terminal(data: dict):
    """Print Phase 1 literature summary to console."""
    papers = data.get("papers_analyzed", [])
    if papers:
        table = Table(title="Phase 1: Analyzed Literature & Downloaded PDFs", header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Title", style="bold", max_width=40)
        table.add_column("Year", justify="center", width=6)
        table.add_column("Source", width=10)
        table.add_column("Local PDF Status", style="green", max_width=25)

        for idx, item in enumerate(papers, 1):
            p = item.get("paper", {})
            local_pdf = p.get("local_pdf_path")
            pdf_status = Path(local_pdf).name if local_pdf else "[dim]No PDF[/dim]"
            table.add_row(
                str(idx),
                p.get("title", "Untitled")[:40],
                str(p.get("year") or "-"),
                p.get("source", "-"),
                pdf_status[:25]
            )
        console.print(table, "\n")


def display_phase2_in_terminal(data: dict):
    """Print Phase 2 chapter ranking tables to console."""
    top_reads = data.get("top_recommended_reading", [])
    if top_reads:
        exec_table = Table(title="Phase 2: Best Rated Chapter by Category (Rank #1)", header_style="bold green")
        exec_table.add_column("Chapter Category", style="bold cyan", width=30)
        exec_table.add_column("Best Paper (Rank 1)", style="bold", max_width=40)
        exec_table.add_column("Score", justify="center", width=10, style="bold yellow")
        exec_table.add_column("Rationale", max_width=40)
        for r in top_reads:
            exec_table.add_row(
                r.get("chapter_type", "")[:30],
                r.get("best_paper", "")[:40],
                r.get("score", ""),
                r.get("reason", "")[:40]
            )
        console.print(exec_table, "\n")

    rankings = data.get("chapter_rankings", {})
    if rankings:
        for cat_key in ["introduction", "methodology", "experiments"]:
            cat_data = rankings.get(cat_key)
            if not cat_data:
                continue
            cat_table = Table(
                title=f"Ranked {cat_data.get('display_name')} (Decreasing Order of Relevance)",
                header_style="bold magenta"
            )
            cat_table.add_column("Rank", justify="center", width=6, style="bold")
            cat_table.add_column("Paper Title", style="bold", max_width=38)
            cat_table.add_column("Score", justify="center", width=8, style="yellow")
            cat_table.add_column("Heading", width=18)
            cat_table.add_column("Extracted Paragraphs", justify="center", width=12)
            cat_table.add_column("Rationale", max_width=35)

            for entry in cat_data.get("ranked_entries", []):
                cat_table.add_row(
                    f"#{entry.get('rank')}",
                    entry.get("paper_title", "")[:38],
                    f"{entry.get('relevance_score', 0):.1f}",
                    entry.get("heading", "")[:18],
                    f"{len(entry.get('extracted_paragraphs', []))} paras",
                    entry.get("ranking_rationale", "")[:35]
                )
            console.print(cat_table, "\n")


def main():
    parser = argparse.ArgumentParser(description="Multi-Skill Academic Research Agent")
    parser.add_argument("--topic", "-t", type=str, help="Subject/topic to research")
    parser.add_argument("--max-papers", "-m", type=int, default=10, help="Max papers to fetch and download (capped at 100 max)")
    parser.add_argument("--sources", "-s", nargs="+", default=["arxiv", "semantic_scholar"], help="Search sources")
    parser.add_argument("--papers-dir", type=str, default="papers", help="Directory where downloaded PDF files are saved")
    parser.add_argument("--phases", "-p", nargs="+", type=int, default=[1, 2, 3, 4], help="Phases to execute (1, 2, 3, 4)")
    parser.add_argument("--output-dir", "-o", type=str, default="outputs", help="Directory to save reports")

    args = parser.parse_args()

    topic = args.topic
    if not topic:
        console.print("[bold yellow]Enter research subject or topic:[/bold yellow] ", end="")
        try:
            topic = input().strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\nExiting.")
            sys.exit(0)

    if not topic:
        console.print("[red]Error: Research subject cannot be empty.[/red]")
        sys.exit(1)

    phases_to_run = sorted(set(args.phases))
    console.print(Panel(
        f"[bold cyan]Academic Research Agent Pipeline[/bold cyan]\n"
        f"Topic: [bold]{topic}[/bold]\n"
        f"Executing Phases: [bold green]{phases_to_run}[/bold green]",
        expand=False
    ))

    # Initialize agent and register all skills
    agent = ResearchAgent(name="MasterResearchAgent")
    agent.register_skill(PaperSearchAndExtractionSkill())
    agent.register_skill(ChapterRankingSkill())
    agent.register_skill(IntroductionWriterSkill())
    agent.register_skill(RelatedWorkWriterSkill())
    agent.register_skill(MethodologyWriterSkill())
    agent.register_skill(ExperimentsWriterSkill())
    agent.register_skill(ConclusionWriterSkill())
    agent.register_skill(LatexPaperCompilerSkill())

    skill_name_map = {
        1: ["paper_search_and_extraction"],
        2: ["chapter_ranking_and_synthesis"],
        3: [
            "introduction_writer",
            "related_work_writer",
            "methodology_writer",
            "experiments_writer",
            "conclusion_writer",
        ],
        4: ["latex_paper_compiler"],
    }

    selected_skills = []
    for p in phases_to_run:
        if p in skill_name_map:
            selected_skills.extend(skill_name_map[p])

    # Run the multi-phase pipeline
    initial_context = {
        "topic": topic,
        "max_papers": min(max(1, args.max_papers), 100),
        "sources": args.sources,
        "papers_dir": args.papers_dir,
    }

    context = agent.run_pipeline(
        skill_names=selected_skills,
        initial_context=initial_context
    )

    # Display Phase 1 & 2 terminal outputs
    if "paper_search_and_extraction" in context:
        display_phase1_in_terminal(context["paper_search_and_extraction"])

    p2_data = context.get("chapter_ranking_and_synthesis") or context.get("literature_synthesis")
    if p2_data:
        display_phase2_in_terminal(p2_data)

    # Display Phase 4 compiled paper info
    if "final_compiled_pdf" in context:
        pdf_path = context["final_compiled_pdf"]
        console.print(Panel(
            f"[bold green]IEEE Conference Research Paper Compiled Successfully![/bold green]\n\n"
            f"• [bold]PDF Document:[/bold] [cyan]{pdf_path}[/cyan]\n"
            f"• [bold]LaTeX Source:[/bold] [cyan]{Path(pdf_path).parent / 'main.tex'}[/cyan]\n"
            f"• [bold]BibTeX Database:[/bold] [cyan]{Path(pdf_path).parent / 'references.bib'}[/cyan]\n"
            f"• [bold]Document Class:[/bold] IEEEtran.cls (2-column conference format)",
            title="Publication Deliverable",
            expand=False
        ))
        console.print()

    # Save comprehensive dossier
    output_dir = Path(args.output_dir)
    json_path, md_path = save_comprehensive_report(output_dir, topic, context)
    console.print(f"[green][+] Full research dossier saved to:[/green] [bold]{json_path}[/bold]")
    console.print(f"[green][+] Full Markdown report saved to:[/green] [bold]{md_path}[/bold]\n")


if __name__ == "__main__":
    main()
