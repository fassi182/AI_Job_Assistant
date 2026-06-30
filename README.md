# AI Job Application Assistant

This project is a full-stack AI assistant for turning a candidate's resume and a target job posting into a personalized application package. It uses FastAPI on the backend, Streamlit on the frontend, and a LangGraph workflow to orchestrate the job analysis and content generation steps.

## What it does

The app lets a user:
- upload an existing resume PDF
- provide a job URL, job description, and/or a screenshot of a job ad
- optionally share company and profile details for better personalization
- receive:
  - a tailored application email subject and body
  - a tailored resume summary, skills, experience bullets, and project bullets

## Project structure

```text
ai-job-application-assistant/
├── backend/
│   ├── main.py                  # FastAPI entrypoint and API routes
│   ├── config.py                # Environment-based settings
│   ├── requirements.txt
│   ├── graph/
│   │   ├── state.py             # LangGraph shared state
│   │   ├── workflow.py          # Compiled LangGraph workflow
│   │   └── nodes/               # Workflow nodes
│   ├── models/
│   │   └── schemas.py           # Pydantic response models
│   ├── services/                # LLM, scraping, and PDF helpers
│   └── storage/                 # Upload and output folders
├── frontend/
│   └── app.py                   # Streamlit frontend UI
├── workflow_diagram.ipynb       # Notebook for visualizing the LangGraph workflow
└── README.md
```

## LangGraph workflow

The workflow currently follows this sequence:

```text
extract_resume -> extract_job_image -> parse_job -> research_company -> optimize_resume -> generate_email
```

Each step is implemented as a node in the LangGraph graph and can be inspected or visualized with the included notebook.

## Setup

1. Create a `.env` file in the project root with at least:

```env
GROQ_API_KEY=your_groq_api_key
```

Optional settings for tracing:

```env
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ai-job-application-assistant
```

2. Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

3. Start the backend:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. In a second terminal, install and run the frontend:

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

5. Open the Streamlit UI in your browser and generate an application.

## Workflow notebook

To inspect the LangGraph workflow visually, run:

```bash
jupyter notebook workflow_diagram.ipynb
```

## Notes

The app is designed to be easy to extend. You can add more nodes to the workflow, improve the resume tailoring logic, or connect additional services for deeper job research and enrichment.
