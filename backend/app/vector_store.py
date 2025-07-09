"""
Local vector store and semantic search for job listings using MongoDB and Hugging Face embeddings.
GCP Dataflow/Vertex AI/Cloud Storage code is scaffolded and commented for future cloud migration.
"""

# --- Local Setup ---
# The following code is configured for local development using MongoDB and Hugging Face embeddings.
# To enable cloud integration, uncomment the GCP-related sections below and configure your GCP credentials.

from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
import numpy as np

# --- GCP Integration (Commented for Local Development) ---
# Uncomment the following imports and functions to enable GCP integration.
# Ensure you have the necessary GCP services set up and credentials configured.
# from google.cloud import storage, aiplatform
# import apache_beam as beam

# def add_job_gcp(job_dict):
#     # Upload job to GCS, trigger Dataflow pipeline for embedding/vectorization
#     pass
#
# def search_jobs_gcp(query, top_k=5):
#     # Use Vertex AI Matching Engine or similar for semantic search
#     pass

# --- Local MongoDB Setup ---
client = MongoClient("mongodb://localhost:27017/")
db = client["job_search"]
jobs_col = db["jobs"]

# --- Embedding Model (local Hugging Face) ---
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

# --- Local: Add job with embedding ---
def add_job_local(job_dict):
    text = job_dict["description"]
    embedding = model.encode(text).tolist()
    job_dict["embedding"] = embedding
    jobs_col.insert_one(job_dict)

# --- Local: Semantic search ---
def search_jobs_local(query, top_k=5):
    query_emb = model.encode(query)
    jobs = list(jobs_col.find())
    scored = []
    for job in jobs:
        emb = np.array(job["embedding"])
        score = float(np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb)))
        scored.append((score, job))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [job for score, job in scored[:top_k]]

# Usage example (local):
# add_job_local({"title": "ML Engineer", "description": "Build ML pipelines..."})
# results = search_jobs_local("machine learning pipelines")
# for job in results:
#     print(job["title"], job["description"])
