import csv
from typing import List, Dict, Any
import re
import logging
import requests
from bs4 import BeautifulSoup
import random

# Get module logger
logger = logging.getLogger("job_search_app.utils")

def export_to_csv(jobs: List[Dict[str, Any]], file_path: str) -> bool:
    """
    Export job listings to CSV file
    
    Args:
        jobs: List of job dictionaries
        file_path: Path to save the CSV file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not jobs:
            logger.warning("No jobs to export")
            return False
            
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = jobs[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for job in jobs:
                writer.writerow(job)
                
        logger.info(f"CSV file saved to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error exporting to CSV: {str(e)}", exc_info=True)
        return False

def extract_skills_from_url(url: str) -> List[str]:
    """
    Extract skills from job URL by scraping the job description page
    
    Args:
        url: Job listing URL
        
    Returns:
        List of extracted skills
    """
    skills = []
    common_skills = [
        'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 
        'node.js', 'express', 'django', 'flask', 'fastapi', 'spring', 'html', 'css',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'sql', 'nosql',
        'mongodb', 'postgresql', 'mysql', 'oracle', 'rest', 'graphql', 'api',
        'agile', 'scrum', 'kanban', 'ci/cd', 'jenkins', 'github actions',
        'machine learning', 'deep learning', 'nlp', 'data science', 'tensorflow', 'pytorch',
        'pandas', 'numpy', 'scikit-learn', 'excel', 'tableau', 'power bi'
    ]
    
    try:
        logger.info(f"Extracting skills from URL: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Failed to retrieve URL: {url}, status code: {response.status_code}")
            return skills
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the main content (job description)
        job_description = ""
        
        # Try different selectors for job descriptions
        if 'linkedin.com' in url.lower():
            description_elem = soup.find('div', class_=re.compile('description'))
            if description_elem:
                job_description = description_elem.get_text()
        elif 'indeed.com' in url.lower():
            description_elem = soup.find('div', id='jobDescriptionText')
            if description_elem:
                job_description = description_elem.get_text()
        else:
            # Generic extraction - look for common job description containers
            description_elem = (
                soup.find('div', class_=re.compile('description')) or
                soup.find('div', class_=re.compile('job-desc')) or
                soup.find('div', class_=re.compile('details'))
            )
            if description_elem:
                job_description = description_elem.get_text()
        
        if not job_description:
            # If all else fails, get the entire page text
            job_description = soup.get_text()
            
        # Look for skills in the job description
        for skill in common_skills:
            skill_pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(skill_pattern, job_description, re.IGNORECASE):
                skills.append(skill)
                
        logger.info(f"Extracted {len(skills)} skills from job URL")
        return skills
        
    except Exception as e:
        logger.error(f"Error extracting skills from URL: {str(e)}", exc_info=True)
        return skills

def create_relevant_jobs(resume_skills: List[str], requested_job_title: str = "") -> List[Dict[str, Any]]:
    """
    Create relevant fallback job listings based on resume skills
    
    Args:
        resume_skills: List of skills extracted from resume
        requested_job_title: Optional job title requested by the user
        
    Returns:
        List of job dictionaries
    """
    logger.info(f"Creating relevant fallback jobs based on {len(resume_skills)} skills")
    
    # Calculate which skills to use in fallback jobs
    top_skills = resume_skills[:min(10, len(resume_skills))]
    if len(top_skills) < 3 and len(resume_skills) > 0:
        top_skills = resume_skills  # Use all skills if we have fewer than 3
    
    logger.info(f"Using top skills for job creation: {', '.join(top_skills)}")
    
    # Prepare job titles based on skills or use the requested one
    tech_job_titles = [
        "Software Engineer", 
        "Full Stack Developer",
        "Backend Developer", 
        "Frontend Developer", 
        "DevOps Engineer",
        "Data Scientist",
        "Machine Learning Engineer",
        "AI Engineer",
        "Data Engineer",
        "Cloud Solutions Architect"
    ]
    
    job_titles = [requested_job_title] if requested_job_title else []
    # Add some variety if we don't have a specific requested title
    if not requested_job_title:
        # Try to infer job title from skills
        if any(skill in ['machine learning', 'tensorflow', 'pytorch', 'deep learning', 'nlp'] for skill in resume_skills):
            job_titles.append("Machine Learning Engineer")
            job_titles.append("AI Engineer")
        elif any(skill in ['react', 'angular', 'vue', 'html', 'css', 'javascript'] for skill in resume_skills):
            job_titles.append("Frontend Developer")
            job_titles.append("UI Engineer")
        elif any(skill in ['python', 'java', 'spring', 'node.js', 'c++', 'go', 'rust'] for skill in resume_skills):
            job_titles.append("Backend Engineer")
            job_titles.append("Software Developer")
        elif any(skill in ['aws', 'azure', 'gcp', 'docker', 'kubernetes'] for skill in resume_skills):
            job_titles.append("Cloud Engineer")
            job_titles.append("DevOps Engineer")
        
        # If we couldn't infer from skills, use some generic titles
        if not job_titles:
            job_titles = random.sample(tech_job_titles, min(3, len(tech_job_titles)))
    
    # Create company names
    tech_companies = [
        "TechCorp Solutions", 
        "InnovateSoft Inc.",
        "Cloudera Systems",
        "DataMind Analytics",
        "FutureTech AI",
        "NexGen Software",
        "Quantum Computing Group",
        "Bright Innovations",
        "CodeCraft Technologies",
        "Stellar IT Solutions"
    ]
    
    companies = random.sample(tech_companies, min(5, len(tech_companies)))
    
    # Create locations
    locations = [
        "Remote, United States",
        "San Francisco, CA",
        "New York, NY",
        "Seattle, WA",
        "Austin, TX",
        "Boston, MA",
        "Chicago, IL"
    ]
    
    # Generate fallback job listings
    jobs = []
    num_jobs = min(5, len(job_titles) * len(companies))  # Create up to 5 jobs
    
    for i in range(num_jobs):
        job_title = job_titles[i % len(job_titles)]
        company = companies[i % len(companies)]
        location = locations[i % len(locations)]
          # Create a relevant job description using the resume skills
        primary_skills = random.sample(top_skills, min(3, len(top_skills)))
        secondary_skills = [skill for skill in top_skills if skill not in primary_skills]
        
        # Add some general technology categories based on the primary skills
        tech_categories = []
        if any(skill in ['python', 'java', 'javascript', 'c++', 'c#'] for skill in primary_skills):
            tech_categories.append("backend development")
        if any(skill in ['react', 'angular', 'vue', 'html', 'css'] for skill in primary_skills):
            tech_categories.append("frontend development")
        if any(skill in ['aws', 'azure', 'gcp', 'docker', 'kubernetes'] for skill in primary_skills):
            tech_categories.append("cloud infrastructure")
        if any(skill in ['machine learning', 'tensorflow', 'pytorch', 'nlp'] for skill in primary_skills):
            tech_categories.append("machine learning")
        
        # Default category if none matched
        if not tech_categories:
            tech_categories = ["software development"]
        
        # Format the skills lists
        primary_skills_text = ", ".join(primary_skills)
        
        # Create different job experience requirements based on job title
        experience_years = "3+"
        if "senior" in job_title.lower() or "lead" in job_title.lower():
            experience_years = "5+"
        elif "junior" in job_title.lower():
            experience_years = "1+"
        
        # Generate random job descriptions based on templates
        job_templates = [
            f"""
            # Job Title: {job_title}
            
            {company} is seeking a talented {job_title} to join our growing team. The ideal candidate will have strong experience with {primary_skills_text} and be passionate about building innovative solutions in {random.choice(tech_categories)}.
            
            ## About Us
            At {company}, we're dedicated to building cutting-edge technology solutions that solve real-world problems. Our team of engineers works collaboratively to develop robust, scalable systems that meet the needs of our clients and users.
            
            ## Responsibilities
            - Design, develop, and maintain software applications using {primary_skills[0] if primary_skills else "relevant technologies"}
            - Collaborate with cross-functional teams to implement new features and improve existing ones
            - Participate in code reviews and contribute to software architecture discussions
            - Write clean, maintainable, and well-tested code
            - Troubleshoot and debug issues in production applications
            - Mentor junior team members and contribute to team knowledge sharing
            
            ## Requirements
            - {experience_years} years of professional experience in {random.choice(tech_categories)}
            - Strong proficiency in {primary_skills_text}
            - Experience with {', '.join(secondary_skills) if secondary_skills else "related technologies"}
            - Bachelor's degree in Computer Science, Engineering, or equivalent practical experience
            - Strong problem-solving skills and attention to detail
            - Excellent communication and collaboration skills
            
            ## Preferred Qualifications
            - Experience with agile development methodologies
            - Understanding of CI/CD pipelines and DevOps principles
            - Knowledge of system design and architecture patterns
            
            ## Benefits
            - Competitive salary and benefits package
            - Remote-friendly work environment
            - Professional development opportunities
            - Collaborative and innovative team culture
            """,
            
            f"""
            # {job_title} Position
            
            ## Company Overview
            {company} is at the forefront of {random.choice(tech_categories)}, building innovative solutions that make a difference. We're looking for a passionate {job_title} to join our growing team and help us continue to push the boundaries of what's possible.
            
            ## Role Description
            As a {job_title}, you'll work on challenging problems, collaborating with a team of talented engineers to build and maintain our core products. You'll have the opportunity to make significant contributions to our codebase and help shape the future of our technology.
            
            ## Key Responsibilities
            - Develop and implement new features using {primary_skills_text}
            - Optimize application performance and scalability
            - Design and implement APIs and services that power our applications
            - Collaborate with product managers and designers to refine requirements
            - Participate in technical planning and architectural decisions
            - Mentor junior developers and contribute to team growth
            
            ## Required Skills
            - {experience_years} years of experience in {random.choice(tech_categories)}
            - Proficiency in {primary_skills_text}
            - Experience with software design patterns and best practices
            - Ability to write clean, testable, and efficient code
            - Strong understanding of data structures and algorithms
            - Bachelor's degree in Computer Science or related field
            
            ## Nice-to-Have Skills
            - Experience with {', '.join(secondary_skills) if secondary_skills else "additional relevant technologies"}
            - Knowledge of microservice architecture
            - Experience with cloud platforms (AWS, Azure, GCP)
            
            ## What We Offer
            - Competitive compensation package
            - Flexible work arrangements
            - Health and wellness benefits
            - Continuous learning opportunities
            """,
        ]
        
        # Choose a random template
        description = random.choice(job_templates)
          # Create a mock application URL based on the company name
        mock_url = ""
        company_domain = company.lower().split()[0].replace(",", "").replace(".", "")
        
        if "tech" in company_domain or "software" in company_domain:
            mock_url = f"https://careers.{company_domain}.example.com/jobs/{job_title.lower().replace(' ', '-')}"
        else:
            mock_url = f"https://www.{company_domain}.example.com/careers/{job_title.lower().replace(' ', '-')}"
            
        jobs.append({
            'title': job_title,
            'company': company,
            'location': location,
            'description': description,
            'url': mock_url,
            'is_fallback': True  # Mark this as a fallback job
        })
    
    logger.info(f"Created {len(jobs)} relevant fallback job listings")
    return jobs
