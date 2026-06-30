"""
Node 5: Generate a personalized, ready-to-send application email using the
resume, the job requirements, the company research, and the candidate's
own supplied details (name, target role, portfolio/GitHub/LinkedIn links).
The LLM writes the body text only; the signature with links is appended
deterministically afterward so links are never garbled or dropped.
"""
import json
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import GraphState
from graph.nodes._utils import safe_json_parse
from services.llm import get_llm

SYSTEM_PROMPT = """You are an expert career coach writing a job application
email on behalf of a candidate. Write a concise, professional, and
personalized email body (150-250 words) that:
- References the specific role and company by name
- Connects the candidate's real background to the company's mission/work
- Highlights 2-3 of the candidate's most relevant strengths for this role,
  drawn ONLY from the candidate_summary/candidate_skills/candidate_experience
  given to you — never invent experience
- Has a confident, warm, non-generic tone (avoid cliches like "I am
  excited to apply" or "I am writing to express my interest")
- Naturally mentions that the candidate's portfolio/GitHub/LinkedIn are
  attached/linked below if those are provided (don't repeat the raw URLs
  inline, they'll be added in a signature block)
- Ends with a clear, simple call to action
- Do NOT include a signature, greeting closer ("Best regards" etc.), or
  the candidate's name at the bottom — that's appended separately

Respond ONLY with valid JSON, no markdown fences:
{
  "subject": "string",
  "body": "string (the email body only, no signature)"
}"""


def generate_email_node(state: GraphState) -> GraphState:
    resume_data = state["resume_data"]
    job_info = state["job_info"]
    company_info = state["company_info"]
    optimized = state["optimized_content"]

    candidate_name = state.get("candidate_name") or resume_data.contact_info.get("name", "")
    target_role = state.get("target_role") or job_info.title

    payload = {
        "candidate_name": candidate_name,
        "candidate_summary": optimized.summary,
        "candidate_skills": optimized.skills,
        "candidate_experience_highlights": optimized.experience[:3],
        "target_role": target_role,
        "job_title": job_info.title,
        "company_name": company_info.name,
        "company_overview": company_info.overview,
        "company_mission": company_info.mission,
        "job_responsibilities": job_info.responsibilities,
        "has_portfolio": bool(state.get("portfolio_url")),
        "has_github": bool(state.get("github_url")),
        "has_linkedin": bool(state.get("linkedin_url")),
    }

    llm = get_llm(temperature=0.6)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(payload)),
    ]
    response = llm.invoke(messages)

    subject = f"Application for {job_info.title} at {company_info.name}".strip()
    body = response.content
    try:
        parsed = safe_json_parse(response.content)
        subject = parsed.get("subject", subject)
        body = parsed.get("body", body)
    except (json.JSONDecodeError, TypeError):
        errors = state.get("errors", []) + ["Failed to parse email JSON; using raw model output as body."]
        signature_lines = ["", "Best regards,", candidate_name or "[Your Name]"]
        if state.get("portfolio_url"):
            signature_lines.append(f"Portfolio: {state['portfolio_url']}")
        if state.get("github_url"):
            signature_lines.append(f"GitHub: {state['github_url']}")
        if state.get("linkedin_url"):
            signature_lines.append(f"LinkedIn: {state['linkedin_url']}")
        if state.get("candidate_email"):
            signature_lines.append(state["candidate_email"])

        tailored_resume = {
            "summary": optimized.summary,
            "experience": optimized.experience,
            "projects": optimized.projects,
            "skills": optimized.skills,
        }
        full_body = body.strip() + "\n" + "\n".join(signature_lines)
        return {
            "email_subject": subject,
            "email_body": full_body,
            "tailored_resume": tailored_resume,
            "errors": errors,
        }

    # Deterministically append a signature block so links are always
    # correct, regardless of what the LLM produced.
    signature_lines = ["", "Best regards,", candidate_name or "[Your Name]"]
    if state.get("portfolio_url"):
        signature_lines.append(f"Portfolio: {state['portfolio_url']}")
    if state.get("github_url"):
        signature_lines.append(f"GitHub: {state['github_url']}")
    if state.get("linkedin_url"):
        signature_lines.append(f"LinkedIn: {state['linkedin_url']}")
    if state.get("candidate_email"):
        signature_lines.append(state["candidate_email"])

    tailored_resume = {
        "summary": optimized.summary,
        "experience": optimized.experience,
        "projects": optimized.projects,
        "skills": optimized.skills,
    }
    full_body = body.strip() + "\n" + "\n".join(signature_lines)
    return {
        "email_subject": subject,
        "email_body": full_body,
        "tailored_resume": tailored_resume,
    }
