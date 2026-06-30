"""
Node 4: Rewrite the summary, experience bullets, project bullets, and skill
ordering to better match the target job — without inventing new experience
or skills that aren't already present in the original resume.
"""
import json
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import GraphState
from graph.nodes._utils import safe_json_parse
from models.schemas import OptimizedResumeContent
from services.llm import get_llm

SYSTEM_PROMPT = """You are an expert resume writer and ATS optimization
specialist. You will be given a candidate's existing resume content and a
target job's requirements. Rewrite ONLY the following fields to better
match the job, while staying strictly truthful to the candidate's real
background:

- summary: a tailored 2-4 sentence professional summary
- experience: rewritten versions of the given experience bullets, same
  number of entries, emphasizing relevant achievements and keywords
- projects: rewritten versions of the given project bullets, same number
  of entries, emphasizing relevant technologies/outcomes
- skills: the candidate's existing skills, REORDERED so the most relevant
  ones to the job appear first. Do not add skills the candidate does not
  have, do not remove any.

CRITICAL RULES:
- Never fabricate employers, titles, dates, degrees, or skills not present
  in the original resume.
- Keep the same factual claims, only change phrasing/emphasis/keywords.
- Respond ONLY with valid JSON, no markdown fences, matching:
{
  "summary": "string",
  "experience": ["string", ...],
  "projects": ["string", ...],
  "skills": ["string", ...]
}"""


def optimize_resume_node(state: GraphState) -> GraphState:
    resume_data = state["resume_data"]
    job_info = state["job_info"]

    payload = {
        "candidate_summary": resume_data.summary,
        "candidate_experience": resume_data.experience,
        "candidate_projects": resume_data.projects,
        "candidate_skills": resume_data.skills,
        "target_role": state.get("target_role") or job_info.title,
        "job_title": job_info.title,
        "job_responsibilities": job_info.responsibilities,
        "job_required_skills": job_info.required_skills,
        "job_technologies": job_info.technologies,
        "job_qualifications": job_info.qualifications,
    }

    llm = get_llm(temperature=0.4)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(payload)),
    ]
    response = llm.invoke(messages)

    optimized = OptimizedResumeContent(
        summary=resume_data.summary,
        experience=resume_data.experience,
        projects=resume_data.projects,
        skills=resume_data.skills,
    )
    try:
        parsed = safe_json_parse(response.content)
        optimized.summary = parsed.get("summary", optimized.summary)
        optimized.experience = parsed.get("experience", optimized.experience)
        optimized.projects = parsed.get("projects", optimized.projects)
        optimized.skills = parsed.get("skills", optimized.skills)
    except (json.JSONDecodeError, TypeError):
        errors = state.get("errors", []) + ["Failed to parse resume optimization JSON; using original content."]
        return {"optimized_content": optimized, "errors": errors}

    return {"optimized_content": optimized}
