from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PaperReference(BaseModel):
    """Structured academic reference/citation."""
    title: str
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    venue: Optional[str] = None
    paper_id: Optional[str] = None
    citation_text: Optional[str] = None


class PaperMetadata(BaseModel):
    """Metadata for an academic paper."""
    paper_id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    abstract: str = ""
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    citation_count: Optional[int] = None
    source: str = "unknown"  # "arxiv", "semantic_scholar", etc.
    references: List[PaperReference] = Field(default_factory=list)


class ExtractedPaperAnalysis(BaseModel):
    """Analysis and extracted knowledge from a paper."""
    paper: PaperMetadata
    core_problem: str = ""
    methodology: str = ""
    key_findings: List[str] = Field(default_factory=list)
    main_ideas: List[str] = Field(default_factory=list)
    key_references_highlighted: List[str] = Field(default_factory=list)
    limitations: Optional[str] = None


class SearchAndExtractionOutput(BaseModel):
    """Final output data structure for the Phase 1 skill."""
    query: str
    total_found: int
    papers_analyzed: List[ExtractedPaperAnalysis] = Field(default_factory=list)
    aggregated_references: List[PaperReference] = Field(default_factory=list)
    top_recurring_references: List[Dict[str, Any]] = Field(default_factory=list)
