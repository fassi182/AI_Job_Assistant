"""
Node 6: Map the optimized content back onto the original resume's text
blocks (by matching old text to its bbox/font/page) and write a new PDF
that preserves layout, fonts, and colors.
"""
import os
import uuid
from difflib import SequenceMatcher
from graph.state import GraphState
from services.pdf_writer import replace_block_text
from config import settings


def _best_match_block(target_text: str, blocks: list) -> dict | None:
    """Finds the resume text block most similar to a given original
    content string, so we know which bbox to overwrite."""
    best, best_score = None, 0.0
    for block in blocks:
        score = SequenceMatcher(None, target_text.strip(), block["text"].strip()).ratio()
        if score > best_score:
            best, best_score = block, score
    return best if best_score > 0.4 else None


def generate_pdf_node(state: GraphState) -> GraphState:
    from services.pdf_extractor import extract_resume_blocks

    blocks = extract_resume_blocks(state["resume_pdf_path"])
    resume_data = state["resume_data"]
    optimized = state["optimized_content"]

    replacements = []

    # Summary
    if resume_data.summary:
        match = _best_match_block(resume_data.summary, blocks)
        if match:
            replacements.append({**match, "new_text": optimized.summary})

    # Experience bullets (matched one-to-one by original text)
    for old, new in zip(resume_data.experience, optimized.experience):
        match = _best_match_block(old, blocks)
        if match:
            replacements.append({**match, "new_text": new})

    # Project bullets
    for old, new in zip(resume_data.projects, optimized.projects):
        match = _best_match_block(old, blocks)
        if match:
            replacements.append({**match, "new_text": new})

    # Skills (joined as one block, replacing the original skills text block)
    if resume_data.skills:
        old_skills_text = ", ".join(resume_data.skills)
        match = _best_match_block(old_skills_text, blocks)
        if match:
            replacements.append({**match, "new_text": ", ".join(optimized.skills)})

    output_filename = f"optimized_resume_{uuid.uuid4().hex[:8]}.pdf"
    output_path = os.path.join(settings.output_dir, output_filename)

    replace_block_text(
        pdf_path=state["resume_pdf_path"],
        output_path=output_path,
        replacements=replacements,
    )

    return {"optimized_resume_path": output_path}
