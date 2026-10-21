from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SkillResult(BaseModel):
    """Standard container for the output of any skill execution."""
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    summary: Optional[str] = None


class BaseSkill(ABC):
    """
    Abstract base class for all skills in the agent pipeline.
    Each phase in the project implements this interface.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, context: Dict[str, Any], **kwargs) -> SkillResult:
        """
        Execute the skill logic given the shared agent context and kwargs.
        
        Args:
            context: Shared dictionary maintaining state across skill executions.
            **kwargs: Extra parameters passed to the skill.
            
        Returns:
            SkillResult indicating success/failure and the resulting data.
        """
        pass

    def __repr__(self) -> str:
        return f"<Skill: {self.name}>"
