"""
Node 2: Parse the job posting from whatever combination of inputs the user
gave us — a URL, a pasted description, and/or text extracted from a job-ad
screenshot — into a structured JobInfo object.
"""
import json
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import GraphState
from graph.nodes._utils import safe_json_parse
from models.schemas import JobInfo
from services.web_scraper import fetch_page_text
from services.llm import get_llm

SYSTEM_PROMPT = """You are a job posting parser. Given raw job posting text,
extract structured fields. Respond ONLY with valid JSON, no markdown
fences, matching this schema:
{
  "title": "string",
  "company": "string",
  "location": "string",
  "responsibilities": ["string", ...],
  "required_skills": ["string", ...],
  "technologies": ["string", ...],
  "qualifications": ["string", ...]
}"""


def parse_job_node(state: GraphState) -> GraphState:
    # Combine every source of job info the user provided. job_description
    # may already include image-extracted text from extract_job_image_node.
    text_parts = []
    if state.get("job_url"):
        try:
            text_parts.append(fetch_page_text(state["job_url"]))
        except Exception:
            errors = state.get("errors", [])
            errors.append(f"Could not fetch job_url: {state['job_url']}")
            state["errors"] = errors
    if state.get("job_description"):
        text_parts.append(state["job_description"])

    raw_text = "\n\n".join(p for p in text_parts if p).strip()

    llm = get_llm(temperature=0)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=raw_text[:12000]),
    ]
    response = llm.invoke(messages)

    job_info = JobInfo(raw_description=raw_text)
    try:
        parsed = safe_json_parse(response.content)
        job_info.title = parsed.get("title", "")
        job_info.company = parsed.get("company", "")
        job_info.location = parsed.get("location", "")
        job_info.responsibilities = parsed.get("responsibilities", [])
        job_info.required_skills = parsed.get("required_skills", [])
        job_info.technologies = parsed.get("technologies", [])
        job_info.qualifications = parsed.get("qualifications", [])
    except (json.JSONDecodeError, TypeError):
        errors = state.get("errors", []) + ["Failed to parse job posting JSON."]
        return {"job_info": job_info, "errors": errors}

    return {"job_info": job_info}
