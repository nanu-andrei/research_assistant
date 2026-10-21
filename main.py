import os
import sys
import json
import argparse
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from agents.agent import ResearchAgent
from first_phase.skill import PaperSearchAndExtractionSkill

console = Console()


def slugify(text: str) -> str:
    """Generate safe filename slug from text."""
    slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", slug)[:50]


def save_reports(output_dir: Path, topic: str, result_data: dict):
    """Save analysis results as JSON and Markdown report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(topic)

    json_path = output_dir / f"{slug}_analysis.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

    md_path = output_dir / f"{slug}_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Academic Research Report: {topic}\n\n")
        f.write(f"- **Total Papers Analyzed:** {result_data.get('total_found', 0)}\n")
        f.write(f"- **Total References Aggregated:** {len(result_data.get('aggregated_references', []))}\n\n")

        f.write("## 1. Analyzed Papers & Key Ideas\n\n")
        for idx, item in enumerate(result_data.get("papers_analyzed", []), 1):
            paper = item.get("paper", {})
            f.write(f"### {idx}. {paper.get('title')}\n")
            f.write(f"- **Authors:** {', '.join(paper.get('authors', []))}\n")
            f.write(f"- **Year:** {paper.get('year') or 'N/A'}\n")
            if paper.get("url"):
                f.write(f"- **URL:** [{paper.get('url')}]({paper.get('url')})\n")
            if paper.get("pdf_url"):
                f.write(f"- **PDF:** [{paper.get('pdf_url')}]({paper.get('pdf_url')})\n")
            f.write(f"- **Source:** `{paper.get('source')}`\n\n")

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

        top_refs = result_data.get("top_recurring_references", [])
        if top_refs:
            f.write("## 2. Most Influential / Recurring Citations\n\n")
            f.write("| Reference Title | Occurrences Across Retrieved Papers |\n")
            f.write("|---|---|\n")
            for r in top_refs:
                f.write(f"| {r.get('reference')} | {r.get('citation_frequency_in_sample')} |\n")
            f.write("\n")

    return json_path, md_path


def display_results_in_terminal(result_data: dict):
    """Print high-level summary tables to the terminal using rich."""
    table = Table(title="Analyzed Literature Summary", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="bold", max_width=45)
    table.add_column("Year", justify="center", width=6)
    table.add_column("Source", width=12)
    table.add_column("Citations", justify="right", width=10)

    for idx, item in enumerate(result_data.get("papers_analyzed", []), 1):
        p = item.get("paper", {})
        table.add_row(
            str(idx),
            p.get("title", "Untitled"),
            str(p.get("year") or "-"),
            p.get("source", "-"),
            str(p.get("citation_count") if p.get("citation_count") is not None else "-")
        )

    console.print("\n", table, "\n")

    top_refs = result_data.get("top_recurring_references", [])
    if top_refs:
        ref_table = Table(title="Top Recurring Foundational References in Sample", header_style="bold cyan")
        ref_table.add_column("Citation / Reference", style="italic")
        ref_table.add_column("Recurrence Count", justify="center", width=18)
        for r in top_refs[:7]:
            ref_table.add_row(r.get("reference", ""), str(r.get("citation_frequency_in_sample", 1)))
        console.print(ref_table, "\n")


def main():
    parser = argparse.ArgumentParser(description="Multi-Skill Academic Research Agent")
    parser.add_argument("--topic", "-t", type=str, help="Subject/topic to research")
    parser.add_argument("--max-papers", "-m", type=int, default=3, help="Max papers to fetch and analyze (default: 3)")
    parser.add_argument("--sources", "-s", nargs="+", default=["arxiv", "semantic_scholar"], help="Search sources")
    parser.add_argument("--extract-pdf", action="store_true", help="Download and extract full-text PDF")
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

    console.print(Panel(f"[bold cyan]Academic Research Agent[/bold cyan]\nTopic: [bold]{topic}[/bold]", expand=False))

    # Initialize agent and register Phase 1 skill
    agent = ResearchAgent(name="MasterResearchAgent")
    agent.register_skill(PaperSearchAndExtractionSkill())

    # Execute Phase 1 skill
    result = agent.run_skill(
        "paper_search_and_extraction",
        topic=topic,
        max_papers=args.max_papers,
        sources=args.sources,
        extract_pdf_text=args.extract_pdf
    )

    if not result.success:
        console.print(f"[bold red]Skill execution failed:[/bold red] {result.error}")
        sys.exit(1)

    # Display results in console
    display_results_in_terminal(result.data)

    # Save reports
    output_dir = Path(args.output_dir)
    json_path, md_path = save_reports(output_dir, topic, result.data)
    console.print(f"[green]✓ Analysis data saved to:[/green] [bold]{json_path}[/bold]")
    console.print(f"[green]✓ Markdown report saved to:[/green] [bold]{md_path}[/bold]\n")


if __name__ == "__main__":
    main()
