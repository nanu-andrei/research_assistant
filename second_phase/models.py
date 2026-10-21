from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RankedChapterEntry(BaseModel):
    """A ranked chapter/section from a paper in decreasing order of relevance and importance."""
    rank: int
    paper_title: str
    paper_id: str
    year: Optional[int] = None
    relevance_score: float  # e.g. 0 - 100
    ranking_rationale: str
    heading: str = ""
    extracted_paragraphs: List[str] = Field(default_factory=list)  # At least 3-4 relevant paragraphs


class ChapterCategoryRanking(BaseModel):
    """Rankings across all reviewed papers for a specific major chapter type."""
    category_key: str      # "introduction", "related_work", "methodology", "experiments", "conclusion"
    display_name: str      # e.g. "Introductions", "Methodologies & System Architectures"
    description: str
    ranked_entries: List[RankedChapterEntry] = Field(default_factory=list)  # Decreasing order by relevance


class ChapterRankingOutput(BaseModel):
    """Output schema for Phase 2: Chapter-Level Relevance & Importance Ranking."""
    topic: str
    total_papers_evaluated: int
    chapter_rankings: Dict[str, ChapterCategoryRanking] = Field(default_factory=dict)
    top_recommended_reading: List[Dict[str, str]] = Field(default_factory=list)
