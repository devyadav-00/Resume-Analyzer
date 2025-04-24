# app/api/fastapi_app.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.preprocessing.preprocess import preprocess_text
from src.embeddings.generate_embeddings import generate_embedding
from src.matching.cosine_similarity import compute_similarity

from PyPDF2 import PdfReader
from io import BytesIO

app = FastAPI()

# Enable CORS (important if connecting with a frontend like Streamlit or React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_pdf(file_bytes):
    reader = PdfReader(BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


@app.post("/match")
async def match_resume_job(resume: UploadFile = File(...), job_desc: UploadFile = File(...)):
    try:
        # Resume reading
        if resume.content_type == "application/pdf":
            resume_text = read_pdf(await resume.read())
        else:
            resume_text = (await resume.read()).decode("utf-8")

        # Job description reading
        if job_desc.content_type == "application/pdf":
            job_desc_text = read_pdf(await job_desc.read())
        else:
            job_desc_text = (await job_desc.read()).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read files: {e}")

    try:
        # Preprocess
        resume_processed = preprocess_text(resume_text)
        job_desc_processed = preprocess_text(job_desc_text)

        # Embedding
        resume_embedding = generate_embedding(resume_processed)
        job_desc_embedding = generate_embedding(job_desc_processed)

        # Similarity
        similarity_score = compute_similarity(resume_embedding, job_desc_embedding)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {e}")

    return {
        "similarity_score": round(similarity_score, 4),
        "message": "Resume matched successfully with job description."
    }
