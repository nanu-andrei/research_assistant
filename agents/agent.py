from typing import Dict, Any, List, Optional
from rich.console import Console
from agents.base_skill import BaseSkill, SkillResult
from agents.llm_client import LLMClient

console = Console()


class ResearchAgent:
    """
    Modular Agent that coordinates and runs skills across different phases.
    Maintains shared context and state across executions.
    """

    def __init__(self, name: str = "AcademicResearchAgent", llm_client: Optional[LLMClient] = None):
        self.name = name
        self.skills: Dict[str, BaseSkill] = {}
        self.context: Dict[str, Any] = {}
        self.llm_client = llm_client or LLMClient()

    def register_skill(self, skill: BaseSkill) -> None:
        """Register a new skill into the agent's capability registry."""
        self.skills[skill.name] = skill
        console.print(f"[green]✓ Registered skill:[/green] [bold]{skill.name}[/bold] - {skill.description}")

    def run_skill(self, skill_name: str, **kwargs) -> SkillResult:
        """Execute a specific registered skill by name."""
        if skill_name not in self.skills:
            error_msg = f"Skill '{skill_name}' not found. Available skills: {list(self.skills.keys())}"
            console.print(f"[red]Error:[/red] {error_msg}")
            return SkillResult(success=False, error=error_msg)

        skill = self.skills[skill_name]
        console.print(f"\n[cyan]▶ Running skill:[/cyan] [bold]{skill.name}[/bold]...")

        try:
            result = skill.execute(self.context, **kwargs)
            if result.success:
                # Merge returned data into agent context
                self.context[skill.name] = result.data
                console.print(f"[green]✓ Completed skill:[/green] [bold]{skill.name}[/bold]")
                if result.summary:
                    console.print(f"  [dim]{result.summary}[/dim]")
            else:
                console.print(f"[red]✗ Skill failed:[/red] {skill.name} - {result.error}")
            return result
        except Exception as e:
            console.print(f"[red]✗ Exception during skill execution:[/red] {e}")
            return SkillResult(success=False, error=str(e))

    def run_pipeline(self, skill_names: Optional[List[str]] = None, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run a pipeline of skills sequentially.
        If skill_names is None, runs all registered skills in registration order.
        """
        if initial_context:
            self.context.update(initial_context)

        execution_order = skill_names or list(self.skills.keys())
        console.print(f"\n[bold blue]=== Starting Agent Pipeline ({len(execution_order)} skills) ===[/bold blue]")

        for name in execution_order:
            result = self.run_skill(name)
            if not result.success:
                console.print(f"[yellow]Pipeline halted at skill '{name}' due to error.[/yellow]")
                break

        console.print("\n[bold blue]=== Pipeline Finished ===[/bold blue]")
        return self.context
