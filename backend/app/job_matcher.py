from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import logging
from .matcher import (
    compute_embeddings, 
    extract_structured_resume, 
    extract_job_requirements, 
    calculate_advanced_match_score
)

logger = logging.getLogger("job_search_app.job_matcher")

class JobMatcher:
    """A class for matching resumes to job descriptions using a combination of
    symbolic matching and embedding-based semantic similarity.
    """
    
    def __init__(self, use_cross_encoder: bool = True):
        """
        Initialize the JobMatcher
        
        Args:
            use_cross_encoder: Whether to use a cross-encoder model for reranking (optional)
        """
        self.use_cross_encoder = use_cross_encoder
        self.cross_encoder = None
        
        # Load cross-encoder model if requested
        if use_cross_encoder:
            try:
                from sentence_transformers import CrossEncoder
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device=device)
                logger.info(f"Successfully loaded CrossEncoder model on device: {device}")
            except Exception as e:
                logger.error(f"Error loading CrossEncoder model: {str(e)}")
                self.use_cross_encoder = False
    
    def match_resume_to_jobs(
        self, 
        resume_text: str, 
        job_texts: List[str],
        job_titles: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Match a resume to multiple job descriptions
        
        Args:
            resume_text: The full text of the resume
            job_texts: List of job description texts
            job_titles: Optional list of job titles
            limit: Maximum number of matches to return
            
        Returns:
            List of job match results with scores and metadata
        """
        # Extract structured resume data
        resume_data = extract_structured_resume(resume_text)
        logger.info(f"Extracted {len(resume_data['skills'])} skills from resume")
        
        # Compute embeddings for resume and jobs
        texts_to_embed = [resume_text] + job_texts
        embeddings = compute_embeddings(texts_to_embed)
        
        if len(embeddings) <= 1:  # Check if we have valid embeddings
            logger.warning("Failed to compute embeddings, falling back to symbolic match only")
            resume_embedding = np.array([])
            job_embeddings = np.array([])
        else:
            resume_embedding = embeddings[0]
            job_embeddings = embeddings[1:]
        
        # Process each job and compute match scores
        matches = []
        for i, job_text in enumerate(job_texts):
            job_title = job_titles[i] if job_titles and i < len(job_titles) else ""
            job_data = extract_job_requirements(job_text, job_title)
            
            # Calculate structured match score
            match_data = calculate_advanced_match_score(resume_data, job_data)
            
            # Calculate embedding similarity if available
            embedding_sim = 0.0
            if resume_embedding.size > 0 and i < len(job_embeddings):
                job_emb = job_embeddings[i]
                
                # Normalize vectors for cosine similarity
                resume_norm = resume_embedding / np.linalg.norm(resume_embedding)
                job_norm = job_emb / np.linalg.norm(job_emb)
                
                # Compute cosine similarity
                embedding_sim = float(np.dot(resume_norm, job_norm))
              # Combined score: 80% symbolic score + 20% embedding similarity
            # Giving more weight to structural scoring which includes the new_grad_friendly component
            combined_score = (match_data["overall_score"] * 0.8) + (embedding_sim * 100 * 0.2)
            combined_score = round(combined_score, 2)
            
            # Create match result
            match_result = {
                "job_index": i,
                "job_title": job_title,
                "final_score": combined_score,
                "symbolic_score": match_data["overall_score"],
                "embedding_similarity": embedding_sim,
                "matched_skills": match_data["matched_skills"],
                "matched_preferred": match_data["matched_preferred"],
                "missing_skills": match_data["missing_skills"],
                "experience_match": match_data["experience_match"],
                "new_grad_friendly": match_data["new_grad_friendly"],
                "score_breakdown": match_data["score_breakdown"]
            }
            
            matches.append(match_result)
        
        # Sort by combined score (highest first)
        sorted_matches = sorted(matches, key=lambda x: x["final_score"], reverse=True)
        
        # Rerank top 5 results with cross-encoder if enabled
        if self.use_cross_encoder and self.cross_encoder and len(sorted_matches) > 1:
            top_n = min(5, len(sorted_matches))
            top_matches = sorted_matches[:top_n]
            
            # Prepare sentence pairs for cross-encoder
            sentence_pairs = []
            for match in top_matches:
                job_idx = match["job_index"]
                sentence_pairs.append([resume_text, job_texts[job_idx]])
            
            # Compute cross-encoder scores
            try:
                cross_scores = self.cross_encoder.predict(sentence_pairs)
                
                # Update scores
                for i, match in enumerate(top_matches):
                    cross_score = float(cross_scores[i])
                    # New blended score: 50% original score + 50% cross-encoder score
                    match["final_score"] = round((match["final_score"] * 0.5) + (cross_score * 0.5), 2)
                    match["cross_encoder_score"] = cross_score
                
                # Resort top matches
                top_matches = sorted(top_matches, key=lambda x: x["final_score"], reverse=True)
                
                # Replace top entries in sorted_matches
                sorted_matches = top_matches + sorted_matches[top_n:]
                logger.info(f"Reranked top {len(top_matches)} matches with CrossEncoder")
            except Exception as e:
                logger.error(f"Error using CrossEncoder for reranking: {str(e)}")
        
        # Limit results
        limited_matches = sorted_matches[:limit]
        logger.info(f"Returning {len(limited_matches)} matches")
        
        return limited_matches
    
    def match_resume_to_job_batch(
        self,
        resume_text: str,
        job_batches: List[Tuple[str, str]],  # List of (job_text, job_title) tuples
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Match a resume against a batch of jobs
        
        Args:
            resume_text: The full text of the resume
            job_batches: List of (job_text, job_title) tuples
            limit: Maximum number of matches to return
            
        Returns:
            List of job match results with scores and metadata
        """
        job_texts = [job[0] for job in job_batches]
        job_titles = [job[1] for job in job_batches]
        
        return self.match_resume_to_jobs(resume_text, job_texts, job_titles, limit)
