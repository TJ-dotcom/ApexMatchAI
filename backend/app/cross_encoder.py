from sentence_transformers import CrossEncoder
import numpy as np

# Load a cross-encoder model for re-ranking, always using GPU if available
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device=device)

def rerank_with_cross_encoder(query: str, jobs: list, top_k: int = 5):
    """
    Re-rank job matches using a cross-encoder for more accurate scoring.
    Args:
        query: The user's resume or extracted skills as a string.
        jobs: List of job dicts with 'description' or 'title'.
        top_k: Number of top results to return.
    Returns:
        List of (score, job) tuples, sorted by score descending.
    """
    pairs = [(query, job['description']) for job in jobs]
    scores = cross_encoder.predict(pairs)
    scored_jobs = list(zip(scores, jobs))
    scored_jobs.sort(reverse=True, key=lambda x: x[0])
    return scored_jobs[:top_k]
