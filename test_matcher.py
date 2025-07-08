#!/usr/bin/env python
# Test script for matcher.py functionality

from backend.app.matcher import extract_job_requirements, extract_structured_resume, calculate_advanced_match_score

def test_senior_job():
    """Test identifying a senior job position"""
    job_text = "This is a Senior Software Engineer role. Requires 5+ years of experience with Python."
    job_title = "Senior Software Engineer II"
    
    result = extract_job_requirements(job_text, job_title)
    print(f"Senior Job Test:")
    print(f"  Experience level: {result['experience_level']}")
    print(f"  Requires Experience: {result['requires_experience']}")
    print(f"  Expected: experience_level=senior, requires_experience=True")
    
def test_junior_job():
    """Test identifying a junior job position"""
    job_text = "This is an entry-level Software Engineer role. No prior experience required."
    job_title = "Junior Software Engineer"
    
    result = extract_job_requirements(job_text, job_title)
    print(f"\nJunior Job Test:")
    print(f"  Experience level: {result['experience_level']}")
    print(f"  Requires Experience: {result['requires_experience']}")
    print(f"  Expected: experience_level=junior, requires_experience=False")
    
def test_mid_job_with_experience():
    """Test identifying a mid-level job requiring 2+ years experience"""
    job_text = "This Software Engineer role requires at least 2 years of experience with React."
    job_title = "Software Engineer"
    
    result = extract_job_requirements(job_text, job_title)
    print(f"\nMid Job with Experience Test:")
    print(f"  Experience level: {result['experience_level']}")
    print(f"  Requires Experience: {result['requires_experience']}")
    print(f"  Expected: experience_level=mid, requires_experience=True")

def test_matching_algorithm():
    """Test the job matching algorithm with new grad focus"""
    # Create a simple resume for a new graduate
    resume_text = """
    Recent Computer Science Graduate
    
    Education:
    Bachelor of Science in Computer Science, University XYZ, 2023
    
    Skills:
    Python, JavaScript, React, SQL, Machine Learning
    
    Projects:
    - Developed a personal website using React
    - Created a machine learning model for image classification
    
    Internship:
    Software Engineering Intern, ABC Corp, Summer 2022
    - Worked on front-end development using React
    - Collaborated with a team of 5 developers
    """
    
    # Test with different job types
    senior_job = {
        "title": "Senior Software Engineer",
        "description": "This role requires 5+ years of experience with Python and JavaScript."
    }
    
    junior_job = {
        "title": "Junior Software Engineer",
        "description": "Entry-level position perfect for new graduates with knowledge of Python."
    }
    
    mid_job_with_exp = {
        "title": "Software Engineer",
        "description": "This role requires at least 2 years of experience with React development."
    }
    
    # Extract structured data
    resume_data = extract_structured_resume(resume_text)
    print("\nResume Data:")
    print(f"  Experience level: {resume_data['experience_level']}")
    print(f"  Skills: {', '.join(resume_data['skills'])}")
    
    # Extract job requirements
    senior_job_data = extract_job_requirements(senior_job["description"], senior_job["title"])
    junior_job_data = extract_job_requirements(junior_job["description"], junior_job["title"])
    mid_job_data = extract_job_requirements(mid_job_with_exp["description"], mid_job_with_exp["title"])
    
    # Calculate match scores
    senior_match = calculate_advanced_match_score(resume_data, senior_job_data)
    junior_match = calculate_advanced_match_score(resume_data, junior_job_data)
    mid_match = calculate_advanced_match_score(resume_data, mid_job_data)
    
    print("\nMatch Scores (higher is better, new grad friendly jobs should score highest):")
    print(f"  Senior job score: {senior_match['overall_score']}")
    print(f"  Junior job score: {junior_match['overall_score']}")
    print(f"  Mid-level job score: {mid_match['overall_score']}")
    print(f"  New grad friendly: Senior={senior_match['new_grad_friendly']}, Junior={junior_match['new_grad_friendly']}, Mid={mid_match['new_grad_friendly']}")
    
    # Verify the scoring priorities are correct
    print("\nScoring Verification:")
    if junior_match['overall_score'] > senior_match['overall_score']:
        print("✓ Junior job correctly scored higher than senior job")
    else:
        print("✗ Junior job did not score higher than senior job")
        
    if junior_match['overall_score'] > mid_match['overall_score']:
        print("✓ Junior job correctly scored higher than mid job requiring experience")
    else:
        print("✗ Junior job did not score higher than mid job requiring experience")

if __name__ == "__main__":
    print("Testing Job Matcher Algorithm with New Graduate Focus")
    print("=" * 50)
    
    # Run tests
    test_senior_job()
    test_junior_job()
    test_mid_job_with_experience()
    test_matching_algorithm()
