import sys
from pathlib import Path
import streamlit as st
import pdfplumber

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

# Custom Imports
from src.preprocessing.preprocess import preprocess_text
from src.model.resume_model import predict_resume_score
from src.components.footer import footer


def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


def main():
    st.set_page_config(page_title="Resume Score Analyzer", page_icon="📄")
    st.title("Resume-to-Job Matcher")

    resume_file = st.file_uploader("Upload Your Resume", type=["pdf", "txt"])

    job_desc_input = st.radio("Provide Job Description:", ("Type/Paste", "Upload File"))
    job_description = ""

    if job_desc_input == "Type/Paste":
        job_description = st.text_area("Enter Job Description:")
    else:
        jd_file = st.file_uploader("Upload Job Description", type=["pdf", "txt"])
        if jd_file:
            job_description = extract_text_from_pdf(jd_file) if jd_file.name.endswith(".pdf") else jd_file.read().decode("utf-8")

    if resume_file:
        resume_text = extract_text_from_pdf(resume_file) if resume_file.name.endswith(".pdf") else resume_file.read().decode("utf-8")
        resume_processed = preprocess_text(resume_text)

        if job_description.strip():
            jd_processed = preprocess_text(job_description)
            st.subheader("ML-Based Resume Score")
            try:
                ml_score = predict_resume_score(resume_processed, jd_processed)
                st.markdown(f"<h1 style='color: #1ed760;'>{ml_score}/100</h1>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"ML Scoring Error: {str(e)}")
        else:
            st.warning("Please provide a Job Description to generate ML-based score.")

    footer()


if __name__ == "__main__":
    main()
