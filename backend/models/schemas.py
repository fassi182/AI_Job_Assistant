"""
Pydantic models shared across the API and the LangGraph workflow.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class JobInfo(BaseModel):
    title: str = ""
    company: str = ""
    location: str = ""
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    raw_description: str = ""


class CompanyInfo(BaseModel):
    name: str = ""
    overview: str = ""
    products: List[str] = Field(default_factory=list)
    mission: str = ""
    values: List[str] = Field(default_factory=list)
    industry: str = ""


class ResumeSection(BaseModel):
    name: str
    text: str
    page_number: int
    bbox: List[float]  # [x0, y0, x1, y1] in PDF coordinates


class ResumeData(BaseModel):
    raw_text: str = ""
    sections: List[ResumeSection] = Field(default_factory=list)
    summary: str = ""
    skills: List[str] = Field(default_factory=list)
    experience: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    contact_info: dict = Field(default_factory=dict)


class OptimizedResumeContent(BaseModel):
    summary: str = ""
    experience: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)


class TailoredResume(BaseModel):
    summary: str = ""
    experience: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    """Info supplied directly by the user, used to fill gaps the resume
    itself doesn't contain (e.g. portfolio link) and to steer tone/targeting."""
    name: Optional[str] = None
    email: Optional[str] = None
    target_role: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class ApplicationRequest(BaseModel):
    job_url: Optional[str] = None
    job_description: Optional[str] = None
    company_website_url: Optional[str] = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    target_role: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class ApplicationResponse(BaseModel):
    email_subject: str
    email_body: str
    tailored_resume: TailoredResume
    optimized_resume_path: Optional[str] = None
    job_info: JobInfo
    company_info: CompanyInfo
