"""
FastAPI entry point. Exposes a single endpoint that runs the full
LangGraph workflow: resume + job info (+ optional job-ad image) + candidate
profile -> tailored email + optimized resume PDF.
"""
import os
import uuid
import shutil
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Get the allowed origin from an environment variable (default to empty list if not set)
# In production, set this to your actual frontend URL, e.g., "https://your-app.streamlit.app"
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "https://aijobassistant-fy4y45ybjh8rpag7mqyjky.streamlit.app/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN], # This now uses the variable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from config import settings
from graph.workflow import app_graph
from models.schemas import ApplicationResponse

app = FastAPI(
    title="AI Job Application Assistant",
    description="Generates personalized application emails and ATS-optimized resumes.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


def _save_upload(upload: UploadFile, prefix: str) -> str:
    ext = os.path.splitext(upload.filename or "")[1] or ""
    filename = f"{prefix}_{uuid.uuid4().hex[:8]}{ext}"
    path = os.path.join(settings.upload_dir, filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return path


@app.post("/api/generate-application", response_model=ApplicationResponse)
async def generate_application(
    resume: UploadFile = File(..., description="Candidate's existing resume, PDF only"),
    job_url: Optional[str] = Form(default=None),
    job_description: Optional[str] = Form(default=None),
    job_image: Optional[UploadFile] = File(default=None, description="Screenshot/photo of the job ad"),
    company_website_url: Optional[str] = Form(default=None),
    candidate_name: Optional[str] = Form(default=None),
    candidate_email: Optional[str] = Form(default=None),
    target_role: Optional[str] = Form(default=None),
    portfolio_url: Optional[str] = Form(default=None),
    github_url: Optional[str] = Form(default=None),
    linkedin_url: Optional[str] = Form(default=None),
):
    if not job_url and not job_description and not job_image:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one of: job_url, job_description, or job_image.",
        )
    if resume.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Resume must be a PDF file.")

    resume_path = _save_upload(resume, "resume")
    job_image_path = None
    if job_image is not None and job_image.filename:
        job_image_path = _save_upload(job_image, "job_ad")

    initial_state = {
        "resume_pdf_path": resume_path,
        "job_url": job_url or None,
        "job_description": job_description or None,
        "job_image_path": job_image_path,
        "company_website_url": company_website_url or None,
        "candidate_name": candidate_name or None,
        "candidate_email": candidate_email or None,
        "target_role": target_role or None,
        "portfolio_url": portfolio_url or None,
        "github_url": github_url or None,
        "linkedin_url": linkedin_url or None,
        "errors": [],
    }

    try:
        result = app_graph.invoke(
            initial_state,
            config={"run_name": "ai_job_application_assistant"},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Workflow failed: {exc}") from exc

    return ApplicationResponse(
        email_subject=result["email_subject"],
        email_body=result["email_body"],
        tailored_resume=result["tailored_resume"],
        job_info=result["job_info"],
        company_info=result["company_info"],
    )


@app.get("/api/download-resume/{filename}")
async def download_resume(filename: str):
    file_path = os.path.join(settings.output_dir, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(file_path, media_type="application/pdf", filename=filename)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.backend_host, port=settings.backend_port, reload=True)
