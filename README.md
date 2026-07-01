# AI Job Application Assistant

AI Job Application Assistant transforms a candidate's resume and job posting information into a personalized application package. The solution uses a Python backend with FastAPI, a Streamlit frontend interface, and a LangGraph workflow to manage the AI agent pipeline.

## Overview

The system accepts:
- a resume PDF upload
- a job posting URL, job description text, and/or a job ad screenshot
- optional company details and candidate profile fields

It produces:
- a customized application email subject and body
- tailored resume content for summary, skills, experience, and projects
- structured job and company insights for better alignment with the role

## Deployments

- Backend deployed on Render: https://ai-job-assistant-oyxg.onrender.com/
- Frontend deployed on Streamlit: https://aijobassistant-ujfmrkkpzuacf5mvuxtuej.streamlit.app/

The Streamlit frontend is configured to use the Render backend URL by default in `frontend/app.py`.

## Architecture

```text
ai-job-application-assistant/
├── backend/
│   ├── main.py                  # FastAPI application and API routes
│   ├── config.py                # environment and runtime settings
│   ├── requirements.txt         # backend dependencies
│   ├── graph/
│   │   ├── state.py             # shared LangGraph state schema
│   │   ├── workflow.py          # compiled LangGraph workflow graph
│   │   └── nodes/               # workflow node implementations
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response models
│   ├── services/                # LLM, scraping, and PDF helper utilities
│   └── storage/                 # upload/output directories
├── frontend/
│   └── app.py                   # Streamlit frontend UI
├── workflow_diagram.ipynb       # visualization notebook for the LangGraph workflow
└── README.md
```

## AI workflow graph

The backend AI agent is implemented as a LangGraph graph. The workflow execution path is:

```text
extract_resume -> extract_job_image -> parse_job -> research_company -> optimize_resume -> generate_email
```

Node responsibilities:
- `extract_resume`: parse resume content from the uploaded PDF
- `extract_job_image`: extract text from an optional job ad image
- `parse_job`: structure job details from URL or pasted description
- `research_company`: enrich company context using the provided site or job data
- `optimize_resume`: generate tailored resume sections for the target role
- `generate_email`: compose a role-specific application email

## Tech stack

- Python
- FastAPI
- Streamlit
- LangGraph
- LangChain / Groq
- LangSmith tracing and monitoring
- Pydantic / pydantic-settings
- requests + BeautifulSoup
- PyMuPDF

## Local setup

1. Create a `.env` file in the project root with required API keys and LangSmith configuration:

```env
GROQ_API_KEY=your_groq_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ai-job-application-assistant
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

2. Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

3. Start the backend locally:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. Install frontend dependencies and run Streamlit:

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

5. Open the frontend in your browser and test the application.

## Notes

This repository is organized to support further workflow extension, improved PDF processing, and richer frontend behavior. The deployed Render backend and Streamlit frontend demonstrate the integrated production endpoints.
