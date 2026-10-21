import os
from typing import List, Optional, Dict, Any
import requests
from first_phase.models import PaperMetadata, PaperReference

S2_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_PAPER_URL = "https://api.semanticscholar.org/graph/v1/paper"

DEFAULT_FIELDS = (
    "paperId,title,authors,year,abstract,citationCount,"
    "openAccessPdf,referenceCount,references.paperId,references.title,"
    "references.authors,references.year,references.venue"
)


def _get_headers() -> Dict[str, str]:
    headers = {"User-Agent": "ResearchAgent/1.0"}
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def search_semantic_scholar(query: str, max_results: int = 5) -> List[PaperMetadata]:
    """
    Search Semantic Scholar Graph API for academic papers.
    """
    params = {
        "query": query.strip(),
        "limit": max_results,
        "fields": DEFAULT_FIELDS,
    }

    try:
        response = requests.get(S2_SEARCH_URL, params=params, headers=_get_headers(), timeout=15)
        if response.status_code == 429:
            print("[Semantic Scholar] Rate limit reached. Proceeding with arXiv results.")
            return []
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[Semantic Scholar Search] Request failed: {e}")
        return []

    papers: List[PaperMetadata] = []
    items = data.get("data", [])
    for item in items:
        papers.append(_parse_s2_paper(item))

    return papers


def fetch_references_for_paper(paper_id_or_arxiv: str) -> List[PaperReference]:
    """
    Fetch references for a paper using its Semantic Scholar ID, DOI, or arXiv ID.
    Example paper_id_or_arxiv: 'ARXIV:2103.00020' or '649def34f8be52c8b66281af98ae772c99cfd5b3'
    """
    url = f"{S2_PAPER_URL}/{paper_id_or_arxiv}"
    params = {"fields": "references.paperId,references.title,references.authors,references.year,references.venue"}

    try:
        response = requests.get(url, params=params, headers=_get_headers(), timeout=15)
        if response.status_code != 200:
            return []
        data = response.json()
        raw_refs = data.get("references", [])
        return _parse_references(raw_refs)
    except Exception as e:
        print(f"[Semantic Scholar References] Could not fetch references for {paper_id_or_arxiv}: {e}")
        return []


def _parse_s2_paper(item: Dict[str, Any]) -> PaperMetadata:
    """Transform Semantic Scholar API object into PaperMetadata."""
    paper_id = item.get("paperId", "")
    title = item.get("title", "Untitled")
    year = item.get("year")
    abstract = item.get("abstract") or ""
    citation_count = item.get("citationCount")

    # Authors
    authors = [a.get("name", "") for a in item.get("authors", []) if a.get("name")]

    # PDF URL
    open_access = item.get("openAccessPdf") or {}
    pdf_url = open_access.get("url")

    # References
    raw_references = item.get("references", [])
    references = _parse_references(raw_references)

    url = f"https://www.semanticscholar.org/paper/{paper_id}" if paper_id else None

    return PaperMetadata(
        paper_id=f"s2:{paper_id}",
        title=title,
        authors=authors,
        year=year,
        abstract=abstract,
        url=url,
        pdf_url=pdf_url,
        citation_count=citation_count,
        source="semantic_scholar",
        references=references,
    )


def _parse_references(raw_references: List[Dict[str, Any]]) -> List[PaperReference]:
    """Parse list of references from Semantic Scholar API."""
    refs: List[PaperReference] = []
    if not raw_references:
        return refs

    for r in raw_references:
        if not r or not r.get("title"):
            continue
        ref_authors = [a.get("name", "") for a in r.get("authors", []) if a.get("name")]
        refs.append(
            PaperReference(
                title=r.get("title", ""),
                authors=ref_authors,
                year=r.get("year"),
                venue=r.get("venue"),
                paper_id=r.get("paperId"),
            )
        )
    return refs
