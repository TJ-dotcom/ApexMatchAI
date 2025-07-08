import os
from typing import List, Dict
import PyPDF2
import docx
import spacy
from pathlib import Path
import logging

# Get module logger
logger = logging.getLogger("job_search_app.resume_parser")

# Load spaCy NLP model
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("Successfully loaded spaCy model 'en_core_web_sm'")
except OSError:
    # If the model is not installed, download it
    logger.warning("spaCy model not found. Attempting to download...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")
    logger.info("Downloaded and loaded spaCy model 'en_core_web_sm'")

def extract_text(file_path: str) -> str:
    """
    Extract text from PDF or DOCX file
    
    Args:
        file_path: Path to the file
        
    Returns:
        Extracted text as a string
    """
    logger.info(f"Extracting text from file: {file_path}")
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.pdf':
        logger.info(f"Detected PDF file format")
        text = extract_text_from_pdf(file_path)
    elif file_ext == '.docx':
        logger.info(f"Detected DOCX file format")
        text = extract_text_from_docx(file_path)
    else:
        logger.error(f"Unsupported file format: {file_ext}")
        raise ValueError(f"Unsupported file format: {file_ext}")
    
    logger.info(f"Text extraction completed. Extracted {len(text)} characters")
    return text


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            logger.info(f"PDF file opened successfully. Contains {len(reader.pages)} pages")
            
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += page_text + "\n"
                logger.info(f"Extracted {len(page_text)} characters from page {i+1}")
        
        logger.info(f"PDF extraction completed successfully")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}", exc_info=True)
        raise


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        logger.info(f"DOCX file opened successfully. Contains {len(doc.paragraphs)} paragraphs")
        
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        logger.info(f"DOCX extraction completed successfully. Extracted {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}", exc_info=True)
        raise


def extract_skills(text: str) -> List[str]:
    """
    Extract skills from text using spaCy NER and noun chunk extraction
    
    Args:
        text: Resume text
        
    Returns:
        List of extracted skills
    """
    logger.info(f"Starting skills extraction from text of length {len(text)}")
    
    # Process the text with spaCy
    skills = []
    try:
        doc = nlp(text)
        logger.info(f"Text processed with spaCy. Document contains {len(doc)} tokens")
        
        # Extract potential skills (nouns and noun phrases)
        
        # Add noun chunks as potential skills
        noun_chunks_count = 0
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 4:  # Limit to phrases of up to 4 words
                skills.append(chunk.text.lower())
                noun_chunks_count += 1
        
        logger.info(f"Extracted {noun_chunks_count} noun chunks as potential skills")
        
        # Add proper nouns (could be technologies, programming languages, etc.)
        proper_nouns_count = 0
        for token in doc:
            if token.pos_ == "PROPN" and len(token.text) > 1:
                skills.append(token.text.lower())
                proper_nouns_count += 1
                
        logger.info(f"Extracted {proper_nouns_count} proper nouns as potential skills")
    except Exception as e:
        logger.error(f"Error during skills extraction: {str(e)}", exc_info=True)
        raise
    
    # Common technical skills keywords (could be expanded)
    tech_skills = [
        'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 
        'node.js', 'express', 'django', 'flask', 'fastapi', 'spring', 'html', 'css',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'sql', 'nosql',
        'mongodb', 'postgresql', 'mysql', 'oracle', 'rest', 'graphql', 'api',
        'agile', 'scrum', 'kanban', 'ci/cd', 'jenkins', 'github actions', 'aws lambda',
        'machine learning', 'deep learning', 'nlp', 'data science', 'tensorflow', 'pytorch',
        'pandas', 'numpy', 'scikit-learn', 'excel', 'tableau', 'power bi'
    ]
    
    # Filter and deduplicate skills
    filtered_skills = list(set([skill for skill in skills if len(skill) > 2]))
    logger.info(f"After filtering and deduplication, found {len(filtered_skills)} potential skills")
    
    # Add any tech skills found in the text that might have been missed
    tech_skills_found = 0
    for skill in tech_skills:
        if skill.lower() in text.lower() and skill not in filtered_skills:
            filtered_skills.append(skill)
            tech_skills_found += 1
    
    logger.info(f"Added {tech_skills_found} additional technical skills found in text")
    logger.info(f"Skills extraction completed. Found total of {len(filtered_skills)} skills")
    
    return filtered_skills
