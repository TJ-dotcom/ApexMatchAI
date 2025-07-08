from typing import List, Tuple, Dict, Any, Set, Optional
import numpy as np
import logging
import re
import spacy
from collections import Counter
from sentence_transformers import SentenceTransformer

# Get module logger
logger = logging.getLogger("job_search_app.matcher")

# Load the sentence transformer model for embeddings
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info(f"Successfully loaded SentenceTransformer model")
except Exception as e:
    logger.error(f"Error loading SentenceTransformer model: {str(e)}", exc_info=True)
    # Create fallback transformer (will not work as well but prevents crash)
    class FallbackTransformer:
        def encode(self, texts, **kwargs):
            logger.warning("Using fallback encoder - results will be random")
            if isinstance(texts, str):
                return np.random.rand(384)  # Single embedding vector
            else:
                return np.random.rand(len(texts), 384)  # Batch of embedding vectors
    
    model = FallbackTransformer()

def compute_embeddings(texts: List[str]) -> np.ndarray:
    """
    Compute embeddings for a list of texts using SentenceTransformer
    
    Args:
        texts: List of text strings
        
    Returns:
        Numpy array of embeddings
    """
    try:
        if not texts:
            logger.warning("No texts provided for embedding computation")
            return np.array([])
            
        embeddings = model.encode(texts, show_progress_bar=False)
        
        logger.info(f"Successfully created {len(embeddings)} embeddings with dimension {embeddings.shape[1]}")
        return embeddings
        
    except Exception as e:
        logger.error(f"Error computing embeddings: {str(e)}", exc_info=True)
        return np.array([])

# Try loading spaCy for better NLP analysis
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("Successfully loaded spaCy model")
except Exception as e:
    logger.error(f"Error loading spaCy model: {e}")
    nlp = None

# Common skill terms by category
TECH_SKILLS = {
    'programming': [
        'python', 'java', 'javascript', 'typescript', 'cpp', 'c++', 'c#', 'go', 'rust', 'php', 
        'ruby', 'swift', 'kotlin', 'scala', 'perl', 'r', 'bash', 'shell'
    ],
    'web_development': [
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'fastapi', 
        'spring', 'asp.net', 'jquery', 'bootstrap', 'tailwind', 'webpack', 'vite'
    ],
    'databases': [
        'sql', 'mysql', 'postgresql', 'mongodb', 'cassandra', 'redis', 'neo4j', 'dynamodb', 'oracle',
        'sqlite', 'mariadb', 'nosql', 'database'
    ],
    'cloud': [
        'aws', 'azure', 'gcp', 'cloud', 'lambda', 's3', 'ec2', 'kubernetes', 'docker', 'terraform', 
        'serverless', 'microservices', 'devops', 'ci/cd', 'jenkins'
    ],
    'ai_ml': [
        'machine learning', 'artificial intelligence', 'deep learning', 'neural networks', 'nlp',
        'computer vision', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
        'matplotlib', 'data science', 'reinforcement learning', 'llm', 'large language model',
        'transformer', 'bert', 'gpt', 'openai', 'langchain', 'rag', 'prompt engineering'
    ],
    'data_engineering': [
        'etl', 'data warehouse', 'data lake', 'spark', 'hadoop', 'kafka', 'airflow', 'databricks',
        'snowflake', 'redshift', 'big data', 'data pipeline', 'data modeling'
    ],
    'soft_skills': [
        'leadership', 'teamwork', 'communication', 'problem-solving', 'time management',
        'critical thinking', 'project management', 'agile', 'scrum', 'kanban'
    ]
}

# Keywords related to different engineering qualities
ENGINEERING_QUALITIES = {
    'product_minded': [
        'user experience', 'user feedback', 'customer', 'product', 'usability', 'feature', 'metric',
        'growth', 'conversion', 'retention', 'engagement', 'satisfaction', 'adoption', 'market',
        'competitive', 'business logic', 'requirement', 'spec', 'specification'
    ],
    'systems_thinking': [
        'architecture', 'system design', 'scale', 'distributed', 'concurrent', 'latency', 'throughput',
        'availability', 'reliability', 'fault-tolerant', 'resilient', 'bottleneck', 'performance',
        'optimization', 'capacity', 'infrastructure'
    ],
    'ownership': [
        'led', 'lead', 'managed', 'built', 'created', 'designed', 'implemented', 'developed',
        'deployed', 'launched', 'owned', 'responsible', 'initiative', 'drove', 'pioneered',
        'established', 'authored', 'spearheaded', 'coordinated'
    ],
    'technical_maturity': [
        'testing', 'test coverage', 'unit test', 'integration test', 'ci/cd', 'pipeline', 'monitoring',
        'logging', 'debugging', 'profiling', 'security', 'code review', 'best practice', 'pattern',
        'architecture', 'design pattern', 'clean code'
    ],
    'learning_adaptability': [
        'learned', 'adapted', 'research', 'studied', 'improved', 'enhanced', 'upgraded', 'migrated',
        'transformed', 'innovated', 'solved', 'overcome', 'experimented', 'prototyped'
    ],
    'impact': [
        'increased', 'decreased', 'reduced', 'improved', 'enhanced', 'saved', 'accelerated',
        'optimized', 'streamlined', 'automated', 'eliminated', 'percent', '%', 'million', 'thousand',
        'impact', 'result', 'outcome', 'success', 'achievement', 'milestone', 'growth', 'revenue'
    ]
}

def extract_structured_resume(resume_text: str) -> Dict[str, Any]:
    """
    Extract structured information from resume text
    
    Args:
        resume_text: The full text of the resume
        
    Returns:
        Dictionary with structured resume information
    """
    try:
        # Use spaCy for better text analysis if available
        if nlp:
            doc = nlp(resume_text)
            
            # Extract potential job titles
            title_candidates = []
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PRODUCT"]:
                    title_candidates.append(ent.text)
            
            # Extract education details
            education_section = re.search(r'(?i)education.*?\n(.*?)(?:\n\n|\Z)', resume_text, re.DOTALL)
            education = education_section.group(1) if education_section else ""
            
            # Extract all skills
            skills = set()
            for category, category_skills in TECH_SKILLS.items():
                for skill in category_skills:
                    if re.search(r'\b' + re.escape(skill) + r'\b', resume_text, re.IGNORECASE):
                        skills.add(skill.lower())
            
            # Extract potential work experience
            experience_section = re.search(r'(?i)(experience|work|employment).*?\n(.*?)(?:\n\n|\Z)', resume_text, re.DOTALL)
            experience = experience_section.group(2) if experience_section else ""
            
            # Count engineering qualities mentioned
            qualities = {}
            for quality, terms in ENGINEERING_QUALITIES.items():
                quality_count = 0
                for term in terms:
                    quality_count += len(re.findall(r'\b' + re.escape(term) + r'\b', resume_text, re.IGNORECASE))
                qualities[quality] = quality_count
            
            # Look for key phrases indicating levels of experience
            experience_level = "unknown"
            if re.search(r'(?i)\b(senior|lead|manager|director|head|architect)\b', resume_text):
                experience_level = "senior"
            elif re.search(r'(?i)\b(mid|intermediate|experienced|associate)\b', resume_text):
                experience_level = "mid"
            elif re.search(r'(?i)\b(junior|entry|intern|graduate|recent)\b', resume_text):
                experience_level = "junior"
            
            return {
                "title": title_candidates[:3],  # Top 3 title candidates
                "education": education,
                "skills": list(skills),
                "experience": experience,
                "qualities": qualities,
                "experience_level": experience_level
            }
        else:
            # Fallback to basic regex extraction if spaCy is not available
            skills = set()
            for category, category_skills in TECH_SKILLS.items():
                for skill in category_skills:
                    if re.search(r'\b' + re.escape(skill) + r'\b', resume_text, re.IGNORECASE):
                        skills.add(skill.lower())
            
            return {
                "title": [],
                "education": "",
                "skills": list(skills),
                "experience": "",
                "qualities": {},
                "experience_level": "unknown"
            }
            
    except Exception as e:
        logger.error(f"Error extracting structured resume information: {str(e)}", exc_info=True)
        return {
            "title": [],
            "education": "",
            "skills": [],
            "experience": "",
            "qualities": {},
            "experience_level": "unknown"
        }

def extract_job_requirements(job_text: str, job_title: str = "") -> Dict[str, Any]:
    """
    Extract structured requirements from job description
    
    Args:
        job_text: The full text of the job description
        job_title: The job title if available separately
        
    Returns:
        Dictionary with structured job requirements
    """
    try:
        # Extract required keywords
        required_keywords = set()
        
        # Look for requirements section
        req_section = re.search(r'(?i)(requirements|qualifications|what you\'ll need).*?\n(.*?)(?:\n\n|\Z)', job_text, re.DOTALL)
        req_text = req_section.group(2) if req_section else job_text
        
        # Extract mentioned skills
        required_skills = set()
        preferred_skills = set()
        
        # Check for required vs preferred pattern
        for category, category_skills in TECH_SKILLS.items():
            for skill in category_skills:
                skill_pattern = r'\b' + re.escape(skill) + r'\b'
                
                # Check if skill is mentioned as required
                if re.search(r'(?i)(required|must have|necessary).*?' + skill_pattern, job_text):
                    required_skills.add(skill.lower())
                # Check if skill is mentioned as preferred
                elif re.search(r'(?i)(preferred|nice to have|plus|bonus).*?' + skill_pattern, job_text):
                    preferred_skills.add(skill.lower())
                # Otherwise check if it's mentioned at all
                elif re.search(skill_pattern, job_text, re.IGNORECASE):
                    required_skills.add(skill.lower())
        
        # Extract years of experience
        years_pattern = r'(\d+)[\+]?\s*(?:to|-)\s*(\d+)[\+]?\s+years?\s+(?:of)?\s*experience'
        years_match = re.search(years_pattern, job_text)
        
        years_min = 0
        years_max = 0
        if years_match:
            years_min = int(years_match.group(1))
            years_max = int(years_match.group(2))
        else:
            single_year_pattern = r'(\d+)[\+]?\s+years?\s+(?:of)?\s*experience'
            single_year_match = re.search(single_year_pattern, job_text)
            if single_year_match:
                years_min = int(single_year_match.group(1))
                years_max = years_min
                
        # Determine experience level from years or job title
        experience_level = "unknown"
        # Check for senior indicators in job title (including Roman numerals for seniority)
        if years_min >= 5 or re.search(r'(?i)\b(senior|lead|principal|staff|architect)\b|\sII\b|\sIII\b', job_title):
            experience_level = "senior"
        elif years_min >= 2 or not re.search(r'(?i)\b(junior|entry|intern|graduate|new grad)\b', job_title):
            experience_level = "mid"
        elif re.search(r'(?i)\b(junior|entry|intern|graduate|new grad)\b', job_title):
            experience_level = "junior"
            
        # Explicitly flag jobs requiring 2+ years of experience for new grad filtering
        requires_experience = years_min >= 2
        
        # Extract engineering qualities required in the job
        qualities = {}
        for quality, terms in ENGINEERING_QUALITIES.items():
            quality_count = 0
            for term in terms:
                quality_count += len(re.findall(r'\b' + re.escape(term) + r'\b', job_text, re.IGNORECASE))
            qualities[quality] = quality_count
          # Extract degree requirements
        degree_required = re.search(r'(?i)(bachelor|master|phd|degree|bs|ms|ba|education).*?(required|needed|must)', job_text) is not None
        
        return {
            "title": job_title,
            "required_skills": list(required_skills),
            "preferred_skills": list(preferred_skills),
            "experience_min": years_min,
            "experience_max": years_max,
            "experience_level": experience_level,
            "requires_experience": requires_experience,
            "degree_required": degree_required,
            "qualities": qualities
        }
    except Exception as e:
        logger.error(f"Error extracting job requirements: {str(e)}", exc_info=True)
        return {
            "title": job_title,
            "required_skills": [],
            "preferred_skills": [],
            "experience_min": 0,
            "experience_max": 0,
            "experience_level": "unknown",
            "requires_experience": False,
            "degree_required": False,
            "qualities": {}
        }

def calculate_advanced_match_score(resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate a sophisticated match score between resume and job
    
    Args:
        resume_data: Extracted resume information
        job_data: Extracted job requirements
        
    Returns:
        Dictionary with match score and breakdown
    """
    try:
        scores = {}
        
        # Check if the job is new-grad friendly (high priority for new grads)
        is_new_grad_friendly = True
        new_grad_penalty = 0        # Apply penalties for jobs not suitable for new grads
        # Check for "senior", "II", "III", or other seniority markers in job title
        if job_data.get("title") and re.search(r'(?i)\b(senior|lead|principal|staff|architect)\b|[^\w](?:II|III|IV|2|3)[^\w]|[^\w](?:sr)[^\w.]', job_data.get("title", "")):
            is_new_grad_friendly = False
            new_grad_penalty += 40  # 40% penalty
        
        # Check for experience requirements (2+ years)
        if job_data.get("requires_experience", False):
            is_new_grad_friendly = False
            new_grad_penalty += 30  # 30% penalty
            
        scores["new_grad_friendly"] = 100 if is_new_grad_friendly else (100 - new_grad_penalty)
            
        # 1. Skills match (highest weight)
        # Calculate what percent of required skills are in the resume
        required_skills_count = len(job_data["required_skills"])
        if required_skills_count > 0:
            skills_matched = [skill for skill in job_data["required_skills"] if skill in resume_data["skills"]]
            skills_score = (len(skills_matched) / required_skills_count) * 100
        else:
            skills_score = 0
        
        # Bonus for preferred skills
        preferred_skills_count = len(job_data["preferred_skills"])
        if preferred_skills_count > 0:
            preferred_matched = [skill for skill in job_data["preferred_skills"] if skill in resume_data["skills"]]
            preferred_score = (len(preferred_matched) / preferred_skills_count) * 100
        else:
            preferred_score = 0
        
        scores["skills_match"] = min(100, skills_score)  # Cap at 100
        scores["preferred_skills"] = min(100, preferred_score)  # Cap at 100
        
        # 2. Experience level match
        # Perfect match = 100, one level apart = 50, completely mismatched = 0
        exp_levels = {"junior": 1, "mid": 2, "senior": 3, "unknown": 2}  # unknown defaults to mid-level
        resume_level = exp_levels.get(resume_data["experience_level"], 2)
        job_level = exp_levels.get(job_data["experience_level"], 2)
        
        # For new grads, we want to prioritize junior positions
        # So junior > mid > senior instead of perfect matches
        if resume_level == 1:  # Junior level resume
            if job_level == 1:  # Junior level job
                scores["experience_level"] = 100
            elif job_level == 2:  # Mid level job
                scores["experience_level"] = 50
            else:  # Senior level job
                scores["experience_level"] = 0
        else:
            # Normal level matching for non-junior resumes
            level_diff = abs(resume_level - job_level)
            if level_diff == 0:
                scores["experience_level"] = 100
            elif level_diff == 1:
                scores["experience_level"] = 50
            else:
                scores["experience_level"] = 0
        
        # 3. Engineering qualities match (ranges from 0-100)
        # Compare overlap in engineering qualities
        quality_scores = []
        for quality, job_count in job_data["qualities"].items():
            if job_count > 0:  # Job mentions this quality
                resume_count = resume_data["qualities"].get(quality, 0)
                # If resume has more mentions than job, it's a good sign
                if resume_count >= job_count:
                    quality_scores.append(100)
                else:
                    # Otherwise, score based on percentage of mentions
                    quality_scores.append((resume_count / job_count) * 100 if job_count > 0 else 0)
        
        scores["quality_match"] = sum(quality_scores) / len(quality_scores) if quality_scores else 50
          # Compute the overall score with weighted components
        # Skills (25%) + Preferred Skills (10%) + Experience Level (15%) + Qualities (10%) + New Grad Friendly (40%)
        overall_score = (scores["skills_match"] * 0.25) + (scores["preferred_skills"] * 0.1) + \
                       (scores["experience_level"] * 0.15) + (scores["quality_match"] * 0.1) + \
                       (scores["new_grad_friendly"] * 0.4)
        
        # Round to 2 decimal places
        overall_score = round(overall_score, 2)
        
        return {
            "overall_score": overall_score,
            "score_breakdown": scores,
            "matched_skills": [skill for skill in job_data["required_skills"] if skill in resume_data["skills"]],
            "matched_preferred": [skill for skill in job_data["preferred_skills"] if skill in resume_data["skills"]],
            "missing_skills": [skill for skill in job_data["required_skills"] if skill not in resume_data["skills"]],
            "experience_match": resume_data["experience_level"] == job_data["experience_level"],
            "new_grad_friendly": is_new_grad_friendly
        }
    except Exception as e:
        logger.error(f"Error calculating advanced match score: {str(e)}", exc_info=True)
        return {
            "overall_score": 0,
            "score_breakdown": {},
            "matched_skills": [],
            "matched_preferred": [],
            "missing_skills": [],
            "experience_match": False,
            "new_grad_friendly": False
        }

def rank_jobs(resume_embedding: np.ndarray, job_embeddings: np.ndarray, 
              resume_text: str = "", job_texts: List[str] = None, 
              job_titles: List[str] = None, limit: int = 10) -> List[Tuple[int, float]]:
    """
    Rank jobs based on similarity to resume with advanced scoring
    
    Args:
        resume_embedding: Embedding vector of the resume
        job_embeddings: Embedding vectors of job descriptions
        resume_text: Raw text of the resume for advanced matching
        job_texts: List of raw job description texts
        job_titles: List of job titles
        limit: Maximum number of jobs to return
        
    Returns:
        List of tuples (job_index, similarity_score) sorted by similarity
    """
    try:
        # Always include basic embedding similarity if available
        similarities = []
        advanced_scores = []
        
        # Check if we can do embedding similarity
        if resume_embedding.size > 0 and job_embeddings.size > 0:
            logger.info("Computing embedding similarity scores")
            for i, job_emb in enumerate(job_embeddings):
                # Normalize the vectors
                resume_norm = resume_embedding / np.linalg.norm(resume_embedding)
                job_norm = job_emb / np.linalg.norm(job_emb)
                
                # Compute cosine similarity
                similarity = np.dot(resume_norm, job_norm)
                similarities.append((i, similarity))
            
            # Sort by similarity (highest first)
            sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
            
            # If we don't have text for advanced scoring, return embedding similarity results
            if not resume_text or not job_texts:
                # Limit the number of results
                top_matches = sorted_similarities[:limit]
                logger.info(f"Ranked {len(similarities)} jobs with embedding similarity only")
                return top_matches
        
        # If we have both resume text and job texts, use advanced scoring
        if resume_text and job_texts:
            logger.info("Computing advanced match scores")
            
            # Extract structured resume data once
            resume_data = extract_structured_resume(resume_text)
            logger.info(f"Extracted {len(resume_data['skills'])} skills from resume")
            
            # Compute advanced score for each job
            for i, job_text in enumerate(job_texts):
                job_title = job_titles[i] if job_titles and i < len(job_titles) else ""
                job_data = extract_job_requirements(job_text, job_title)
                match_data = calculate_advanced_match_score(resume_data, job_data)
                
                # Use advanced score, or cosine similarity if it's available as fallback
                embedding_score = 0
                for idx, score in similarities:
                    if idx == i:
                        embedding_score = score
                        break
                          # Combine scores: 80% advanced score + 20% embedding similarity
                # Giving more weight to our structural scoring which includes the new_grad_friendly component
                combined_score = (match_data["overall_score"] * 0.8 + embedding_score * 100 * 0.2) / 100
                advanced_scores.append((i, combined_score))
                
                logger.info(f"Job {i}: Advanced score {match_data['overall_score']:.2f}, " + 
                           f"Embedding score {embedding_score:.2f}, Combined {combined_score:.2f}")
            
            # Sort by combined score (highest first)
            sorted_scores = sorted(advanced_scores, key=lambda x: x[1], reverse=True)
            
            # Limit the number of results
            top_matches = sorted_scores[:limit]
            logger.info(f"Ranked {len(advanced_scores)} jobs with advanced scoring")
            return top_matches
            
        # If we only have embedding similarity, use that
        elif similarities:
            top_matches = sorted_similarities[:limit]
            logger.info(f"Ranked {len(similarities)} jobs with embedding similarity only")
            return top_matches
        
        # If we have nothing, return empty list
        logger.warning("No data available for ranking jobs")
        return []
        
    except Exception as e:
        logger.error(f"Error ranking jobs: {str(e)}", exc_info=True)
        return []
