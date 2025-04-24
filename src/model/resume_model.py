# src/model/resume_model.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

model = SentenceTransformer('all-MiniLM-L6-v2')

def clean_text(text):
    text = re.sub(r'\W+', ' ', text.lower())
    tokens = text.split()
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

def predict_resume_score(resume_text, job_desc_text):
    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_desc_text)
    emb_resume = model.encode(resume_clean)
    emb_job = model.encode(job_clean)
    similarity = cosine_similarity([emb_resume], [emb_job])[0][0]
    return round(similarity * 100, 2)  # Return a percentage score
