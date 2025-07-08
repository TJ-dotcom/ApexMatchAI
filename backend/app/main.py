from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, Dict, Any
import os
import uuid
import shutil
from pathlib import Path
import asyncio
import logging

# Import our task storage class
from .task_storage import TaskStorage
import time

# Configure logging
import datetime
log_file = f"./logs/job_search_app_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Keep console output but also log to file
    ]
)
logger = logging.getLogger("job_search_app")
logger.info(f"Starting application. Logging to {log_file}")



# Local semantic search and vector store
from .vector_store import add_job_local, search_jobs_local
# from .vector_store import add_job_gcp, search_jobs_gcp  # Uncomment for GCP
from .resume_parser import extract_text, extract_skills
from .scraper_no_retry import scrape_jobs
from .matcher import compute_embeddings, rank_jobs
from .utils import export_to_csv

app = FastAPI(title="Job Search Resume Matcher")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a directory for uploaded files if it doesn't exist
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create a directory for results if it doesn't exist
RESULTS_DIR = Path("./results")
RESULTS_DIR.mkdir(exist_ok=True)

# Initialize persistent task storage from our imported module
task_storage = TaskStorage()
tasks = task_storage.get_all()

# --- API endpoints for local semantic search ---
@app.post("/jobs/add-local")
async def add_job_api(job: Dict[str, Any]):
    """Add a job to the local MongoDB vector store (local dev)."""
    add_job_local(job)
    return {"status": "ok"}

# @app.post("/jobs/add-gcp")
# async def add_job_api_gcp(job: Dict[str, Any]):
#     """Add a job to the GCP pipeline (commented for local dev)."""
#     add_job_gcp(job)
#     return {"status": "ok"}

@app.get("/jobs/search-local")
async def search_jobs_api(query: str, top_k: int = 5):
    """Semantic search for jobs using local MongoDB and Hugging Face embeddings."""
    results = search_jobs_local(query, top_k)
    for job in results:
        job.pop("embedding", None)
    return {"results": results}

# @app.get("/jobs/search-gcp")
# async def search_jobs_api_gcp(query: str, top_k: int = 5):
#     """Semantic search for jobs using GCP (commented for local dev)."""
#     results = search_jobs_gcp(query, top_k)
#     return {"results": results}

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a directory for uploaded files if it doesn't exist
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create a directory for results if it doesn't exist
RESULTS_DIR = Path("./results")
RESULTS_DIR.mkdir(exist_ok=True)

# Initialize persistent task storage from our imported module
task_storage = TaskStorage()
tasks = task_storage.get_all()


@app.post("/upload")
async def upload_resume(
    resume: UploadFile = File(...),
    job_url: str = Form(...)
):
    # Generate a unique task ID
    task_id = str(uuid.uuid4())
    
    # Save the uploaded file
    file_path = UPLOAD_DIR / f"{task_id}_{resume.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)
    
    # Store task information
    tasks[task_id] = {
        "status": "processing",
        "file_path": str(file_path),
        "job_url": job_url,
        "results": None,
        "csv_path": None
    }
    
    # Start processing in the background
    asyncio.create_task(process_resume_and_jobs(task_id))
    
    return {"task_id": task_id, "status": "processing"}


async def process_resume_and_jobs(task_id: str):
    try:
        task = tasks[task_id]
        file_path = task["file_path"]
        job_url = task["job_url"]
        
        # Extract text from resume
        resume_text = extract_text(file_path)
        if not resume_text:
            raise ValueError("Failed to extract text from resume. The file may be empty or corrupted.")

        # Extract skills from resume
        resume_skills = extract_skills(resume_text)
        
        # Store resume skills for potential use in advanced matching
        import sys
        sys._resume_skills = resume_skills
        logger.info(f"Extracted {len(resume_skills)} skills from resume: {', '.join(resume_skills[:10])}")
        
        # Scrape job listings with enhanced retry mechanisms
        logger.info(f"Initiating job scraping from URL: {job_url} with enhanced retry and anti-detection")
        job_listings = scrape_jobs(job_url)
        
        # Check if we have valid job listings - our enhanced scraper should handle all cases
        if not job_listings:
            logger.error(f"Failed to extract job listings after multiple attempts from URL: {job_url}")
            raise ValueError(f"Could not extract any job listings from URL: {job_url}. Please check if the URL is valid and accessible or try a different job search site.")
        
        # Log scraping results
        logger.info(f"Successfully scraped {len(job_listings)} valid job listings from {job_url}")
        
        # Compute embeddings for resume
        resume_embs = compute_embeddings([resume_text])
        if resume_embs.size == 0:
            raise ValueError("Failed to compute embeddings for resume")
        
        resume_emb = resume_embs[0]
        
        # Compute embeddings for jobs
        job_texts = [job["description"] for job in job_listings]
        job_titles = [job["title"] for job in job_listings]
        job_embs = compute_embeddings(job_texts)
        if job_embs.size == 0:
            raise ValueError("Failed to compute embeddings for job descriptions")
        
        # Rank jobs based on advanced similarity algorithms
        logger.info("Using enhanced job matching algorithm")
        top_matches = rank_jobs(
            resume_embedding=resume_emb, 
            job_embeddings=job_embs, 
            resume_text=resume_text, 
            job_texts=job_texts,
            job_titles=job_titles,
            limit=len(job_listings)
        )
        
        # Create results with scores
        results = []
        for idx, score in top_matches:
            job = job_listings[idx].copy()
            job["match_score"] = float(score)
            results.append(job)
        
        # Export to CSV
        csv_path = RESULTS_DIR / f"{task_id}_results.csv"
        export_to_csv(results, str(csv_path))
        
        # Update task with results
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["results"] = results
        tasks[task_id]["csv_path"] = str(csv_path)
        
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {str(e)}", exc_info=True)
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)


@app.get("/results/{task_id}")
async def get_results(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] == "completed":
        return {
            "status": "completed",
            "results": task["results"],
            "csv_url": f"/download/{task_id}"
        }
    elif task["status"] == "failed":
        return {
            "status": "failed",
            "error": task.get("error", "Unknown error")
        }
    else:
        return {"status": "processing"}


@app.get("/download/{task_id}")
async def download_csv(task_id: str):
    if task_id not in tasks or tasks[task_id]["status"] != "completed":
        raise HTTPException(status_code=404, detail="Results not ready or task not found")
    
    # Serve the file for download
    from fastapi.responses import FileResponse
    csv_path = tasks[task_id]["csv_path"]
    return FileResponse(path=csv_path, filename=f"job_matches_{task_id}.csv", media_type="text/csv")


@app.get("/uploads/{file_id}")
async def serve_uploaded_file(file_id: str):
    """Serve uploaded files directly"""
    try:
        # Log the request
        logging.info(f"Serving file with ID: {file_id}")
        
        # Look for the file in the uploads directory
        matching_files = list(UPLOAD_DIR.glob(f"{file_id}*"))
        
        if not matching_files:
            logging.warning(f"File not found with ID: {file_id}")
            # List available files to help with debugging
            available_files = list(UPLOAD_DIR.glob("*"))
            logging.info(f"Available files: {[f.name for f in available_files]}")
            raise HTTPException(status_code=404, detail=f"File not found with ID: {file_id}")
        
        # If we find a file that starts with the ID, serve it
        file_path = matching_files[0]
        logging.info(f"Found file: {file_path.name}")
        return FileResponse(path=str(file_path))
    except Exception as e:
        logging.error(f"Error serving file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")


@app.get("/")
def read_root():
    return {"message": "Job Search Resume Matcher API"}


@app.get("/debug/tasks")
async def debug_tasks():
    """A debugging endpoint to list all tasks"""
    return {
        "task_count": len(tasks),
        "tasks": {
            task_id: {
                "status": task_info["status"],
                "file_path": task_info["file_path"],
                "job_url": task_info["job_url"],
                "has_results": task_info["results"] is not None,
                "has_csv": task_info["csv_path"] is not None
            } for task_id, task_info in tasks.items()
        }
    }
