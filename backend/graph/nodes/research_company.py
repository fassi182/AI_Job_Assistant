"""
Node 3: Research the hiring company. Prefers the company website URL the
user supplied directly; falls back to guessing it from the job URL's
domain; falls back to LLM knowledge of the company name alone.
"""
import json
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import GraphState
from graph.nodes._utils import safe_json_parse
from models.schemas import CompanyInfo
from services.web_scraper import fetch_page_text, guess_company_homepage
from services.llm import get_llm

SYSTEM_PROMPT = """You are a company research assistant. Given raw website
text (or, if empty, just a company name) produce a brief structured
profile. Respond ONLY with valid JSON, no markdown fences:
{
  "overview": "1-2 sentence overview",
  "products": ["string", ...],
  "mission": "string",
  "values": ["string", ...],
  "industry": "string"
}
If information is unavailable, use empty strings/lists rather than
inventing facts."""


def research_company_node(state: GraphState) -> GraphState:
    job_info = state["job_info"]
    company_name = job_info.company or "the company"

    homepage = state.get("company_website_url")
    if not homepage and state.get("job_url"):
        homepage = guess_company_homepage(state["job_url"])

    raw_text = ""
    errors = state.get("errors", [])
    if homepage:
        try:
            raw_text = fetch_page_text(homepage)
        except Exception:
            errors = errors + [f"Could not fetch company website: {homepage}"]

    llm = get_llm(temperature=0.2)
    user_content = raw_text[:8000] if raw_text else f"Company name: {company_name}"
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]
    response = llm.invoke(messages)

    company_info = CompanyInfo(name=company_name)
    try:
        parsed = safe_json_parse(response.content)
        company_info.overview = parsed.get("overview", "")
        company_info.products = parsed.get("products", [])
        company_info.mission = parsed.get("mission", "")
        company_info.values = parsed.get("values", [])
        company_info.industry = parsed.get("industry", "")
    except (json.JSONDecodeError, TypeError):
        errors = errors + ["Failed to parse company research JSON."]
        return {"company_info": company_info, "errors": errors}

    updates = {"company_info": company_info}
    if errors != state.get("errors", []):
        updates["errors"] = errors
    return updates
