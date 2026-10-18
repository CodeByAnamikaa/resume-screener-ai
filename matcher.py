import io
import re
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILLS_DB = [
    "python", "fastapi", "django", "flask", "javascript", "typescript",
    "react", "next.js", "node.js", "sql", "postgresql", "mysql",
    "mongodb", "docker", "kubernetes", "aws", "git", "machine learning",
    "data structures", "algorithms", "rest api", "ci/cd", "linux"
]

def clean_text(text: str) -> str:
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    stream = io.BytesIO(file_bytes)
    reader = PdfReader(stream)
    extracted = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            extracted += page_text + " "
    return clean_text(extracted)

def extract_matched_and_missing_skills(resume_text: str, jd_text: str):
    resume_clean = resume_text.lower()
    jd_clean = jd_text.lower()
    required_skills = [s for s in SKILLS_DB if s in jd_clean]
    matched_skills = [s for s in required_skills if s in resume_clean]
    missing_skills = [s for s in required_skills if s not in matched_skills]
    return matched_skills, missing_skills

def calculate_match(resume_text: str, job_description: str) -> dict:
    jd_cleaned = clean_text(job_description)
    documents = [resume_text, jd_cleaned]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    matched_skills, missing_skills = extract_matched_and_missing_skills(resume_text, jd_cleaned)
    return {
        "score_percentage": round(float(similarity) * 100, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }