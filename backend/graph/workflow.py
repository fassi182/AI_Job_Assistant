"""
Builds and compiles the LangGraph StateGraph for the full application
pipeline:

  extract_resume -> parse_job -> research_company -> optimize_resume
                                                     -> generate_email
                                                     -> generate_pdf

generate_email and generate_pdf both depend on optimize_resume's output but
not on each other, so they run as parallel branches before joining at END.
"""
from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph.nodes.extract_resume import extract_resume_node
from graph.nodes.extract_job_image import extract_job_image_node
from graph.nodes.parse_job import parse_job_node
from graph.nodes.research_company import research_company_node
from graph.nodes.optimize_resume import optimize_resume_node
from graph.nodes.generate_email import generate_email_node


def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("extract_resume", extract_resume_node)
    workflow.add_node("extract_job_image", extract_job_image_node)
    workflow.add_node("parse_job", parse_job_node)
    workflow.add_node("research_company", research_company_node)
    workflow.add_node("optimize_resume", optimize_resume_node)
    workflow.add_node("generate_email", generate_email_node)

    workflow.set_entry_point("extract_resume")
    workflow.add_edge("extract_resume", "extract_job_image")
    workflow.add_edge("extract_job_image", "parse_job")
    workflow.add_edge("parse_job", "research_company")
    workflow.add_edge("research_company", "optimize_resume")

    workflow.add_edge("optimize_resume", "generate_email")
    workflow.add_edge("generate_email", END)

    return workflow.compile()


# Singleton compiled graph, reused across requests
app_graph = build_graph()
