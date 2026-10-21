import io
import re
from pathlib import Path
from typing import List, Optional, Dict
import requests
from pypdf import PdfReader
from first_phase.models import PaperSection


def sanitize_filename(name: str) -> str:
    """Create a safe filename from a title or ID."""
    clean = re.sub(r'[\\/*?:"<>|]', "", name)
    clean = re.sub(r"\s+", "_", clean).strip("._")
    return clean[:120]


def download_paper_pdf(
    pdf_url: str,
    output_dir: Path,
    filename: str,
    timeout: int = 30
) -> Optional[Path]:
    """
    Download a PDF from a URL and save it to output_dir/filename.
    If the file already exists and is non-empty, re-use existing file (caching).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    if not filename.lower().endswith(".pdf"):
        filename = f"{filename}.pdf"

    target_path = output_dir / filename

    if target_path.exists() and target_path.stat().st_size > 5000:
        return target_path

    headers = {"User-Agent": "AcademicResearchBot/1.0 (+https://github.com/academic-agent)"}
    try:
        response = requests.get(pdf_url, headers=headers, stream=True, timeout=timeout)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()
        if "html" in content_type and "pdf" not in content_type:
            return None

        with open(target_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=16384):
                if chunk:
                    f.write(chunk)

        if target_path.stat().st_size < 2000:
            target_path.unlink(missing_ok=True)
            return None

        return target_path
    except Exception as e:
        print(f"[PDF Downloader] Failed to download from {pdf_url}: {e}")
        if target_path.exists():
            target_path.unlink(missing_ok=True)
        return None


def extract_text_from_local_pdf(pdf_path: Path, max_pages: int = 25) -> str:
    """
    Extract clean text from a locally stored PDF file up to max_pages.
    """
    if not pdf_path or not pdf_path.exists():
        return ""

    try:
        reader = PdfReader(str(pdf_path))
        extracted_pages = []
        total_pages = len(reader.pages)
        pages_to_read = min(total_pages, max_pages)

        for i in range(pages_to_read):
            text = reader.pages[i].extract_text() or ""
            extracted_pages.append(text)

        raw_text = "\n\n".join(extracted_pages)
        # Clean soft hyphen line breaks
        cleaned_text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", raw_text)
        return cleaned_text
    except Exception as e:
        print(f"[PDF Reader] Could not read PDF {pdf_path.name}: {e}")
        return ""


def clean_into_paragraphs(text: str) -> List[str]:
    """
    Split text into clean, substantial paragraphs (filtering out headers, page numbers, short artifacts).
    """
    raw_blocks = re.split(r"\n\s*\n+", text)
    paragraphs = []
    for block in raw_blocks:
        # Normalize internal whitespaces and newlines
        clean_block = " ".join(block.split()).strip()
        # Filter out short lines like headings, figure captions, page numbers (< 80 chars)
        if len(clean_block) >= 80:
            paragraphs.append(clean_block)
    return paragraphs


def select_top_relevant_paragraphs(paragraphs: List[str], topic: str, count: int = 4) -> List[str]:
    """
    Select the top N paragraphs most relevant to the topic based on term frequency and density.
    """
    if not paragraphs:
        return []
    if len(paragraphs) <= count:
        return paragraphs

    topic_terms = [t.lower() for t in re.findall(r"\w+", topic) if len(t) > 2]
    
    scored_paragraphs = []
    for idx, p in enumerate(paragraphs):
        p_lower = p.lower()
        score = sum(p_lower.count(term) * 3 for term in topic_terms)
        # Bonus for containing academic indicator terms
        for ind in ["propose", "method", "result", "accuracy", "performance", "experiment", "novel", "challenge"]:
            if ind in p_lower:
                score += 1
        scored_paragraphs.append((score, idx, p))

    # Sort by score descending, preserving original flow if scores are tied
    scored_paragraphs.sort(key=lambda x: (x[0], -x[1]), reverse=True)
    selected = [item[2] for item in scored_paragraphs[:count]]
    return selected


SECTION_REGEXES = [
    ("introduction", r"\n\s*(?:(?:I|1|1\.)\s+)?(?:INTRODUCTION|Introduction)\b"),
    ("related_work", r"\n\s*(?:(?:II|2|2\.)\s+)?(?:RELATED WORK|Related Work|BACKGROUND|Background|Related Works)\b"),
    ("methodology", r"\n\s*(?:(?:III|3|3\.)\s+)?(?:METHODOLOGY|Methodology|SYSTEM DESIGN|System Design|PROPOSED METHOD|Proposed Method|APPROACH|Approach|METHOD|Method|ARCHITECTURE|Architecture|FRAMEWORK|Framework)\b"),
    ("experiments", r"\n\s*(?:(?:IV|4|4\.)\s+)?(?:EXPERIMENTS|Experiments|EVALUATION|Evaluation|EXPERIMENTAL RESULTS|Experimental Results|PERFORMANCE EVALUATION|RESULTS|Results)\b"),
    ("conclusion", r"\n\s*(?:(?:V|VI|5|6|5\.|6\.)\s+)?(?:CONCLUSION|Conclusion|CONCLUSIONS|Conclusions|DISCUSSION|Discussion|CONCLUDING REMARKS)\b"),
    ("references", r"\n\s*(?:REFERENCES|References|BIBLIOGRAPHY|Bibliography)\b"),
]


def extract_sections_from_pdf_text(full_text: str, topic: str = "") -> Dict[str, PaperSection]:
    """
    Segment paper text into major chapters:
    - introduction
    - related_work
    - methodology
    - experiments
    - conclusion
    For each chapter, extracts the most relevant 3-4 paragraphs.
    """
    sections: Dict[str, PaperSection] = {}
    if not full_text:
        return sections

    # Find matches and character offsets for all sections
    matches = []
    for sec_type, pattern in SECTION_REGEXES:
        m = re.search(pattern, full_text, re.IGNORECASE)
        if m:
            matches.append((m.start(), m.end(), sec_type, m.group(0).strip()))

    matches.sort(key=lambda x: x[0])

    # Extract text slices between matched headers
    for i in range(len(matches)):
        start_pos, header_end, sec_type, heading = matches[i]
        if sec_type == "references":
            continue

        end_pos = matches[i + 1][0] if (i + 1 < len(matches)) else len(full_text)
        sec_text = full_text[header_end:end_pos]
        all_paras = clean_into_paragraphs(sec_text)

        # Select at least 3-4 paragraphs with highest relevance
        selected_paras = select_top_relevant_paragraphs(all_paras, topic, count=4)
        word_count = sum(len(p.split()) for p in selected_paras)

        if selected_paras:
            sections[sec_type] = PaperSection(
                section_category=sec_type,
                heading=heading,
                paragraphs=selected_paras,
                word_count=word_count,
            )

    return sections


def extract_references_from_text(text: str) -> List[str]:
    """
    Heuristically extracts raw reference strings from paper text if references section is found.
    """
    if not text:
        return []

    ref_match = re.search(r"\n\s*(References|BIBLIOGRAPHY|REFERENCES)\s*\n", text, re.IGNORECASE)
    if not ref_match:
        return []

    ref_text = text[ref_match.end():]
    entries = re.split(r"\n\s*(?:\[\d+\]|\d+\.)\s+", ref_text)
    cleaned_entries = [e.strip().replace("\n", " ") for e in entries if len(e.strip()) > 15]
    return cleaned_entries[:50]


def parse_reference_entry(raw_ref: str) -> dict:
    """Parse raw citation string into title, year, and authors."""
    year_match = re.search(r"\b(19\d\d|20\d\d)\b", raw_ref)
    year = int(year_match.group(1)) if year_match else None

    title_match = re.search(r'["“]([^"”]+)["”]', raw_ref)
    if title_match:
        title = title_match.group(1).strip()
    else:
        parts = raw_ref.split(",")
        title = parts[1].strip() if len(parts) > 1 else raw_ref[:80]

    return {
        "title": title,
        "year": year,
        "citation_text": raw_ref,
    }
