"""
Shared state object passed between all LangGraph nodes.
"""
from typing import Optional, TypedDict, List
from models.schemas import ResumeData, JobInfo, CompanyInfo, OptimizedResumeContent, TailoredResume


class GraphState(TypedDict, total=False):
    # Inputs
    resume_pdf_path: str
    job_url: Optional[str]
    job_description: Optional[str]
    job_image_path: Optional[str]
    company_website_url: Optional[str]

    # Candidate-supplied info (fills gaps the resume itself can't tell us)
    candidate_name: Optional[str]
    candidate_email: Optional[str]
    target_role: Optional[str]
    portfolio_url: Optional[str]
    github_url: Optional[str]
    linkedin_url: Optional[str]

    # Intermediate / derived data
    resume_data: ResumeData
    job_info: JobInfo
    company_info: CompanyInfo
    optimized_content: OptimizedResumeContent
    tailored_resume: TailoredResume

    # Outputs
    email_subject: str
    email_body: str
    optimized_resume_path: str

    # Bookkeeping
    errors: List[str]
