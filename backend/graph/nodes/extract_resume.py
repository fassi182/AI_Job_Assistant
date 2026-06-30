"""
Node 1: Extract resume text + layout structure from the uploaded PDF, then
use the LLM to classify content into sections (summary, experience,
projects, skills, education, contact info).
"""
import json
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import GraphState
from services.pdf_extractor import build_resume_data
from services.llm import get_llm

SYSTEM_PROMPT = """You are a resume parsing assistant. Given the raw text of
a resume, extract structured fields. Respond ONLY with valid JSON, no
markdown fences, matching this schema:
{
  "summary": "string",
  "skills": ["string", ...],
  "experience": ["one string per role/bullet group", ...],
  "projects": ["one string per project", ...],
  "education": ["one string per degree/entry", ...],
  "contact_info": {"name": "", "email": "", "phone": "", "location": ""}
}
Do not invent information that is not present in the resume."""


def extract_resume_node(state: GraphState) -> GraphState:
    resume_data = build_resume_data(state["resume_pdf_path"])

    llm = get_llm(temperature=0)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=resume_data.raw_text),
    ]
    response = llm.invoke(messages)

    try:
        parsed = json.loads(response.content)
        resume_data.summary = parsed.get("summary", "")
        resume_data.skills = parsed.get("skills", [])
        resume_data.experience = parsed.get("experience", [])
        resume_data.projects = parsed.get("projects", [])
        resume_data.education = parsed.get("education", [])
        resume_data.contact_info = parsed.get("contact_info", {})
    except (json.JSONDecodeError, TypeError):
        errors = state.get("errors", []) + ["Failed to parse resume classification JSON."]
        return {"resume_data": resume_data, "errors": errors}

    return {"resume_data": resume_data}
