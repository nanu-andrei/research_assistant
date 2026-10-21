import io
import re
from typing import List, Optional, Tuple
import requests
from pypdf import PdfReader


def download_and_extract_pdf_text(pdf_url: str, max_pages: int = 10, timeout: int = 20) -> str:
    """
    Download a PDF from a URL and extract text up to max_pages.
    """
    headers = {"User-Agent": "ResearchAgent/1.0"}
    try:
        response = requests.get(pdf_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)
        
        extracted_pages = []
        total_pages = len(reader.pages)
        pages_to_read = min(total_pages, max_pages)

        for i in range(pages_to_read):
            page_text = reader.pages[i].extract_text() or ""
            extracted_pages.append(page_text)

        return "\n\n".join(extracted_pages)
    except Exception as e:
        print(f"[PDF Reader] Could not read PDF from {pdf_url}: {e}")
        return ""


def extract_references_from_text(text: str) -> List[str]:
    """
    Heuristically extracts raw reference strings from paper text if references section is found.
    """
    if not text:
        return []

    # Look for "References" or "Bibliography" header
    ref_match = re.search(r"\n\s*(References|BIBLIOGRAPHY|REFERENCES)\s*\n", text, re.IGNORECASE)
    if not ref_match:
        return []

    ref_text = text[ref_match.end():]
    # Split by common reference markers like [1], [2], 1., etc.
    entries = re.split(r"\n\s*(?:\[\d+\]|\d+\.)\s+", ref_text)
    cleaned_entries = [e.strip().replace("\n", " ") for e in entries if len(e.strip()) > 15]
    return cleaned_entries[:50]
