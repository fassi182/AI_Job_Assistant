"""
Writes optimized text back into the original resume PDF, preserving layout,
fonts, and design. Strategy: for each block whose text should change,
redact (white-out) the original bbox and insert the new text using the same
font size/color, wrapped to fit within the original box width.
"""
import fitz  # PyMuPDF


def _get_color(color_int: int) -> tuple[float, float, float]:
    return (
        ((color_int >> 16) & 255) / 255,
        ((color_int >> 8) & 255) / 255,
        (color_int & 255) / 255,
    )


def replace_block_text(pdf_path: str, output_path: str, replacements: list[dict]) -> str:
    """
    replacements: list of dicts with keys:
      page_number, bbox [x0,y0,x1,y1], new_text, font, size, color
    Each matching block's old text is redacted and replaced with new_text,
    preserving position, font size, and color as closely as possible.
    """
    doc = fitz.open(pdf_path)
    for rep in replacements:
        page = doc[rep["page_number"]]
        x0, y0, x1, y1 = rep["bbox"]
        rect = fitz.Rect(x0, y0, x1, y1)

        # White-out the original block
        page.add_redact_annot(rect, fill=(1, 1, 1))
        page.apply_redactions()

        font = rep.get("font", "helv")
        size = rep.get("size", 10)
        color = _get_color(rep.get("color", 0))

        try:
            page.insert_textbox(
                rect,
                rep["new_text"],
                fontname=font,
                fontsize=size,
                color=color,
                align=0,
                lineheight=size * 1.2,
            )
        except Exception:
            # Fallback to a basic font if the original font is unavailable.
            page.insert_textbox(
                rect,
                rep["new_text"],
                fontname="helv",
                fontsize=size,
                color=color,
                align=0,
                lineheight=size * 1.2,
            )

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return output_path
