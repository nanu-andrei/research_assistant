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


class PaperSection(BaseModel):
    """Extracted major chapter / section from an academic paper."""
    section_category: str  # "introduction", "related_work", "methodology", "experiments", "conclusion"
    heading: str
    paragraphs: List[str] = Field(default_factory=list)
    word_count: int = 0


class PaperMetadata(BaseModel):
    """Metadata for an academic paper."""
    paper_id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    abstract: str = ""
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    local_pdf_path: Optional[str] = None
    citation_count: Optional[int] = None
    source: str = "unknown"  # "arxiv", "semantic_scholar", etc.
    references: List[PaperReference] = Field(default_factory=list)
    sections: Dict[str, PaperSection] = Field(default_factory=dict)


class ExtractedPaperAnalysis(BaseModel):
    """Analysis and extracted knowledge from a paper."""
    paper: PaperMetadata
    core_problem: str = ""
    methodology: str = ""
    key_findings: List[str] = Field(default_factory=list)
    main_ideas: List[str] = Field(default_factory=list)
    key_references_highlighted: List[str] = Field(default_factory=list)
    limitations: Optional[str] = None
    most_relevant_paragraphs: List[str] = Field(default_factory=list)


class SearchAndExtractionOutput(BaseModel):
    """Final output data structure for the Phase 1 skill."""
    query: str
    total_found: int
    papers_analyzed: List[ExtractedPaperAnalysis] = Field(default_factory=list)
    aggregated_references: List[PaperReference] = Field(default_factory=list)
    top_recurring_references: List[Dict[str, Any]] = Field(default_factory=list)
