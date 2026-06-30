"""
Node 0 (optional): If the user uploaded a screenshot/photo of a job ad
instead of (or in addition to) a URL/description, use a Groq vision model
to read the text out of the image. Its output is merged into
job_description before parsing.
"""
import base64
import mimetypes
from langchain_core.messages import HumanMessage
from graph.state import GraphState
from config import settings
from langchain_groq import ChatGroq

VISION_MODEL = "llama-3.2-90b-vision-preview"


def _image_to_data_url(image_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(image_path)
    mime_type = mime_type or "image/png"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


def extract_job_image_node(state: GraphState) -> GraphState:
    image_path = state.get("job_image_path")
    if not image_path:
        return state

    vision_llm = ChatGroq(api_key=settings.groq_api_key, model=VISION_MODEL, temperature=0)
    data_url = _image_to_data_url(image_path)

    message = HumanMessage(content=[
        {"type": "text", "text": (
            "Transcribe all readable text from this job advertisement image "
            "exactly as it appears (title, company, requirements, "
            "responsibilities, location, etc). Output plain text only."
        )},
        {"type": "image_url", "image_url": {"url": data_url}},
    ])

    errors = state.get("errors", [])
    try:
        response = vision_llm.invoke([message])
        extracted_text = response.content
    except Exception:
        errors = errors + ["Failed to read text from job ad image."]
        extracted_text = ""

    existing_description = state.get("job_description") or ""
    job_description = (existing_description + "\n" + extracted_text).strip()
    updates = {"job_description": job_description}
    if errors != state.get("errors", []):
        updates["errors"] = errors
    return updates
