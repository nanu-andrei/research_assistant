import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Optional
import requests
from first_phase.models import PaperMetadata

ARXIV_API_URL = "http://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def search_arxiv(query: str, max_results: int = 5, sort_by: str = "relevance") -> List[PaperMetadata]:
    """
    Search arXiv for papers matching the given query string.
    
    Args:
        query: Search term or research subject.
        max_results: Maximum number of papers to retrieve.
        sort_by: Ranking strategy ('relevance', 'lastUpdatedDate', 'submittedDate').
        
    Returns:
        List of PaperMetadata objects.
    """
    # Sanitize and format query
    clean_query = query.strip()
    params = {
        "search_query": f"all:{clean_query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": "descending",
    }
    
    headers = {
        "User-Agent": "ResearchAgent/1.0 (academic-research-bot)"
    }
    
    try:
        response = requests.get(ARXIV_API_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"[arXiv Search] Request failed: {e}")
        return []

    return parse_arxiv_atom(response.text)


def parse_arxiv_atom(atom_xml: str) -> List[PaperMetadata]:
    """Parse Atom XML feed response from arXiv API."""
    papers: List[PaperMetadata] = []
    try:
        root = ET.fromstring(atom_xml)
    except ET.ParseError as e:
        print(f"[arXiv Search] Failed to parse XML: {e}")
        return papers

    for entry in root.findall("atom:entry", ATOM_NS):
        # Extract ID (e.g. http://arxiv.org/abs/2103.00020v1 -> 2103.00020)
        id_elem = entry.find("atom:id", ATOM_NS)
        raw_id = id_elem.text.strip() if id_elem is not None and id_elem.text else ""
        paper_id = raw_id.split("/abs/")[-1] if "/abs/" in raw_id else raw_id

        # Title
        title_elem = entry.find("atom:title", ATOM_NS)
        title = " ".join(title_elem.text.split()) if title_elem is not None and title_elem.text else "Untitled"

        # Abstract
        summary_elem = entry.find("atom:summary", ATOM_NS)
        abstract = " ".join(summary_elem.text.split()) if summary_elem is not None and summary_elem.text else ""

        # Published date / year
        published_elem = entry.find("atom:published", ATOM_NS)
        year: Optional[int] = None
        if published_elem is not None and published_elem.text:
            try:
                year = int(published_elem.text[:4])
            except ValueError:
                pass

        # Authors
        authors: List[str] = []
        for author_elem in entry.findall("atom:author", ATOM_NS):
            name_elem = author_elem.find("atom:name", ATOM_NS)
            if name_elem is not None and name_elem.text:
                authors.append(name_elem.text.strip())

        # PDF URL
        pdf_url: Optional[str] = None
        for link in entry.findall("atom:link", ATOM_NS):
            if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                pdf_url = link.attrib.get("href")
                break
        
        # If no explicit pdf link attribute, fallback to replacing /abs/ with /pdf/
        if not pdf_url and raw_id:
            pdf_url = raw_id.replace("/abs/", "/pdf/") + ".pdf"

        papers.append(
            PaperMetadata(
                paper_id=f"arxiv:{paper_id}",
                title=title,
                authors=authors,
                year=year,
                abstract=abstract,
                url=raw_id,
                pdf_url=pdf_url,
                source="arxiv",
                references=[],
            )
        )

    return papers
