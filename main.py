from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging

from matcher import extract_text_from_pdf, calculate_match

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Enterprise AI Resume Screener API")

# Needed so the browser frontend (index.html) can call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

@app.get("/")
def health_check():
    return {"status": "secure_engine_running"}

def process_resume(contents: bytes, job_description: str):
    """CPU-heavy work (PDF parsing + embeddings); runs in a worker thread."""
    resume_text = extract_text_from_pdf(contents)
    if not resume_text:
        return None
    return calculate_match(resume_text, job_description)

@app.post("/screen")
async def screen_resumes(
    job_description: str = Form(...),
    files: List[UploadFile] = File(...),
):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is empty.")
    if not files:
        raise HTTPException(status_code=400, detail="Upload at least one document.")

    results = []
    for file in files:
        if file.content_type != "application/pdf":
            logging.warning(f"Blocked invalid file type attempt: {file.filename}")
            continue

        contents = await file.read()

        if len(contents) > MAX_FILE_SIZE_BYTES:
            logging.warning(f"Blocked oversized payload: {file.filename} ({len(contents)} bytes)")
            continue

        if not contents.startswith(b"%PDF-"):
            logging.warning(f"Blocked file with invalid PDF signature: {file.filename}")
            continue

        try:
            analysis = await run_in_threadpool(process_resume, contents, job_description)
        except Exception:
            logging.exception(f"Failed to process {file.filename}")
            continue

        if analysis is None:
            logging.warning(f"Failed to extract text from verified PDF: {file.filename}")
            continue

        results.append({
            "filename": file.filename,
            "match_score": analysis["score_percentage"],
            "matched_skills": analysis["matched_skills"],
            "missing_skills": analysis["missing_skills"],
        })

    return {"rankings": sorted(results, key=lambda x: x["match_score"], reverse=True)}