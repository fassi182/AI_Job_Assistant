"""
Streamlit frontend for the AI Job Application Assistant.
Collects the candidate's resume + profile links and the job info
(URL, pasted description, and/or a screenshot of the ad), then shows the
generated email and a download link for the tailored resume PDF.
"""
import os
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Job Application Assistant", page_icon="📄", layout="centered")

st.title("📄 AI Job Application Assistant")
st.caption("Get a personalized application email + tailored resume, ready to send.")

with st.form("application_form"):
    st.subheader("Your info")
    col1, col2 = st.columns(2)
    with col1:
        candidate_name = st.text_input("Full name")
        target_role = st.text_input("Target role (optional)", placeholder="e.g. Backend Engineer")
        portfolio_url = st.text_input("Portfolio URL (optional)")
    with col2:
        candidate_email = st.text_input("Your email (for the signature)")
        github_url = st.text_input("GitHub URL (optional)")
        linkedin_url = st.text_input("LinkedIn URL (optional)")

    resume_file = st.file_uploader("Your existing resume (PDF)", type=["pdf"])

    st.subheader("Job info")
    st.caption("Provide any combination: URL, pasted description, and/or a screenshot of the ad.")
    job_url = st.text_input("Job posting URL (optional)")
    job_description = st.text_area("Job description (optional)", height=160)
    job_image = st.file_uploader("Screenshot/photo of the job ad (optional)", type=["png", "jpg", "jpeg"])
    company_website_url = st.text_input("Company website (optional, improves email personalization)")

    submitted = st.form_submit_button("Generate Application", use_container_width=True)

if submitted:
    if not resume_file:
        st.error("Please upload your resume PDF.")
    elif not job_url and not job_description and not job_image:
        st.error("Please provide at least a job URL, a job description, or a job ad screenshot.")
    else:
        with st.spinner("Reading job info, researching company, and tailoring your application..."):
            files = {"resume": (resume_file.name, resume_file.getvalue(), "application/pdf")}
            if job_image:
                files["job_image"] = (job_image.name, job_image.getvalue(), job_image.type)

            data = {
                "job_url": job_url or "",
                "job_description": job_description or "",
                "company_website_url": company_website_url or "",
                "candidate_name": candidate_name or "",
                "candidate_email": candidate_email or "",
                "target_role": target_role or "",
                "portfolio_url": portfolio_url or "",
                "github_url": github_url or "",
                "linkedin_url": linkedin_url or "",
            }
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/generate-application",
                    files=files,
                    data=data,
                    timeout=180,
                )
                response.raise_for_status()
                st.session_state["result"] = response.json()
            except requests.exceptions.RequestException as exc:
                detail = ""
                try:
                    detail = exc.response.json().get("detail", "")
                except Exception:
                    pass
                st.error(f"Request failed: {exc}\n{detail}")

if "result" in st.session_state:
    result = st.session_state["result"]

    st.success("Your tailored application is ready!")

    st.subheader("📌 Job Summary")
    job_info = result["job_info"]
    st.write(f"**Title:** {job_info.get('title', 'N/A')}")
    st.write(f"**Company:** {job_info.get('company', 'N/A')}")
    if job_info.get("required_skills"):
        st.write("**Key skills required:** " + ", ".join(job_info["required_skills"]))

    st.subheader("✉️ Personalized Email")
    st.text_input("Subject", value=result["email_subject"], key="subject")
    st.text_area("Body (copy this into your email client)", value=result["email_body"], height=350, key="body")

    st.subheader("📑 Tailored Resume Sections")
    st.info(
        "Copy each section below into your own resume editor. Keep the original headings, text sizes, and formatting from your resume — replace only the section copy with these tailored sections."
    )

    tailored = result["tailored_resume"]
    st.markdown("**Summary**")
    st.text_area("Tailored Summary", value=tailored.get("summary", ""), height=150, key="tailored_summary")

    st.markdown("**Skills**")
    st.text_area(
        "Tailored Skills",
        value=", ".join(tailored.get("skills", [])),
        height=100,
        key="tailored_skills",
    )

    st.markdown("**Experience**")
    st.text_area(
        "Tailored Experience Bullets",
        value="\n".join(tailored.get("experience", [])),
        height=220,
        key="tailored_experience",
    )

    st.markdown("**Projects**")
    st.text_area(
        "Tailored Projects",
        value="\n".join(tailored.get("projects", [])),
        height=180,
        key="tailored_projects",
    )
