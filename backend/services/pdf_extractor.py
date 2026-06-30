"""
Extracts raw text and per-block layout info (position, font, size) from a
resume PDF using PyMuPDF. This layout info is what allows the PDF writer to
later replace text in place without disturbing the original design.
"""
import fitz  # PyMuPDF
from models.schemas import ResumeData, ResumeSection


def extract_resume_blocks(pdf_path: str) -> list[dict]:
    """Returns a list of text blocks with their page number, bbox, font info
    and text, in reading order."""
    doc = fitz.open(pdf_path)
    blocks_info = []
    for page_number, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block.get("type") != 0:  # skip images
                continue
            text_lines = []
            font_name, font_size, color = "helv", 10, 0
            for line in block.get("lines", []):
                line_text = ""
                for span in line.get("spans", []):
                    line_text += span.get("text", "")
                    font_name = span.get("font", font_name)
                    font_size = span.get("size", font_size)
                    color = span.get("color", color)
                text_lines.append(line_text)
            block_text = "\n".join(text_lines).strip()
            if block_text:
                blocks_info.append({
                    "page_number": page_number,
                    "bbox": list(block["bbox"]),
                    "text": block_text,
                    "font": font_name,
                    "size": font_size,
                    "color": color,
                })
    doc.close()
    return blocks_info


def extract_resume_text(pdf_path: str) -> str:
    """Returns the full plain text of the resume."""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


def build_resume_data(pdf_path: str) -> ResumeData:
    """Builds a ResumeData object with raw text and section blocks.
    Section classification (summary/experience/etc.) is refined later by an
    LLM node, this just captures the structural layout."""
    raw_text = extract_resume_text(pdf_path)
    blocks = extract_resume_blocks(pdf_path)
    sections = [
        ResumeSection(
            name="unclassified",
            text=b["text"],
            page_number=b["page_number"],
            bbox=b["bbox"],
        )
        for b in blocks
    ]
    return ResumeData(raw_text=raw_text, sections=sections)
