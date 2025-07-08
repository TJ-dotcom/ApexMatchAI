import sys
import os
import logging

# Add parent directory to path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

from app.job_matcher import JobMatcher

# Sample resume text (new grad CS student)
sample_resume = """
John Doe
123 Main Street, Anytown, USA
Email: johndoe@example.com
Phone: (123) 456-7890

EDUCATION
University of Technology
Bachelor of Science in Computer Science, Expected May 2025
GPA: 3.8/4.0
Relevant Coursework: Data Structures, Algorithms, Database Systems, Web Development, Machine Learning

TECHNICAL SKILLS
Languages: Python, JavaScript, Java, C++, HTML/CSS, SQL
Frameworks/Libraries: React, Node.js, Express, Flask, TensorFlow, NumPy, Pandas
Tools & Technologies: Git, Docker, AWS, MongoDB, PostgreSQL
Soft Skills: Problem-solving, Teamwork, Communication, Time Management

PROJECTS
Personal Website Portfolio - React, Node.js
- Designed and developed a responsive portfolio website using React and Node.js
- Implemented a contact form with email notification using Express and Nodemailer

Machine Learning Image Classifier - Python, TensorFlow, Keras
- Built and trained a CNN model to classify images with 92% accuracy
- Implemented data augmentation techniques to improve model performance

Online Bookstore Database - SQL, Java, Spring Boot
- Designed and implemented a database schema for an online bookstore
- Created RESTful API endpoints for book browsing and user management

EXPERIENCE
Software Engineering Intern, TechStart Inc.
June 2024 - August 2024
- Developed new features for the company's web application using React and Node.js
- Collaborated with a team of 5 developers using Agile methodology
- Optimized database queries, improving load times by 30%

Teaching Assistant, University of Technology
September 2023 - May 2024
- Assisted professor in teaching Python programming to a class of 50 undergraduate students
- Conducted weekly lab sessions and graded assignments
- Created supplementary learning materials that increased student satisfaction by 25%

LEADERSHIP & ACTIVITIES
Computer Science Club - Vice President
- Organized monthly tech talks and workshops for 100+ club members
- Coordinated a hackathon event with 200+ participants and 10 industry sponsors
"""

# Sample job descriptions
sample_jobs = [
    # Job 1: Junior Frontend Developer
    ("""
    Junior Frontend Developer
    
    About the Role:
    We're looking for an entry-level frontend developer to join our growing team. This is a perfect opportunity for recent graduates or those early in their career.
    
    Requirements:
    - BS/BA in Computer Science or related field (or equivalent experience)
    - Knowledge of HTML, CSS, and JavaScript
    - Experience with React or similar frontend frameworks
    - Basic understanding of responsive design principles
    - Familiarity with Git and version control
    
    Nice to Have:
    - Experience with TypeScript
    - Understanding of CSS preprocessors (Sass, Less)
    - Experience with UI/UX design principles
    - Knowledge of testing frameworks like Jest
    
    About Us:
    We are a fast-growing startup focused on creating intuitive web applications for businesses. Our team values collaboration, continuous learning, and work-life balance.
    """, "Junior Frontend Developer"),
    
    # Job 2: Mid-level Full Stack Engineer
    ("""
    Mid-level Full Stack Engineer
    
    We are looking for a Full Stack Engineer with 3-5 years of experience to join our product development team. The ideal candidate will have strong skills in both frontend and backend development.
    
    Requirements:
    - 3+ years of professional software development experience
    - Proficiency in JavaScript/TypeScript and one backend language (Python, Node.js, Java)
    - Experience with React, Angular, or Vue.js
    - Working knowledge of databases (SQL and NoSQL)
    - Experience with cloud platforms (AWS, GCP, or Azure)
    - Strong understanding of web application architecture
    
    Preferred Skills:
    - Experience with microservices architecture
    - Knowledge of Docker and Kubernetes
    - Understanding of CI/CD pipelines
    - Experience with GraphQL
    
    The role involves designing and implementing new features, optimizing existing functionality, and collaborating with product managers and designers to create intuitive user experiences.
    """, "Mid-level Full Stack Engineer"),
    
    # Job 3: Data Science Intern
    ("""
    Data Science Intern
    
    Join our data science team for a summer internship opportunity! Perfect for students studying computer science, mathematics, or statistics who are interested in machine learning and data analysis.
    
    What You'll Need:
    - Currently pursuing a degree in Computer Science, Mathematics, Statistics or related field
    - Programming experience in Python
    - Knowledge of data manipulation libraries (NumPy, Pandas)
    - Exposure to machine learning concepts and libraries (scikit-learn, TensorFlow)
    - Strong analytical and problem-solving skills
    
    Bonus Points For:
    - Experience with data visualization (Matplotlib, Seaborn, Plotly)
    - Familiarity with SQL and database concepts
    - Previous project experience in machine learning or data analysis
    - Knowledge of statistical analysis techniques
    
    During this internship, you'll work closely with our data scientists on real projects, analyze customer data, build predictive models, and gain hands-on experience in the field.
    """, "Data Science Intern"),
    
    # Job 4: Senior Software Engineer
    ("""
    Senior Software Engineer
    
    We are seeking a Senior Software Engineer with 8+ years of experience to lead our backend development team. The ideal candidate will have a strong background in distributed systems and cloud infrastructure.
    
    Requirements:
    - 8+ years of professional software development experience
    - Deep expertise in Java, Go, or Python
    - Experience building and maintaining high-performance, distributed systems
    - Extensive knowledge of database systems (both SQL and NoSQL)
    - Strong understanding of system design principles and architectural patterns
    - Experience with cloud platforms (AWS preferred)
    - Track record of technical leadership and mentoring junior engineers
    
    Preferred Qualifications:
    - Experience with Kubernetes and container orchestration
    - Knowledge of event-driven architectures and message brokers
    - Experience with infrastructure as code (Terraform, CloudFormation)
    - Background in financial systems or high-security environments
    
    This role involves architectural decision-making, code reviews, performance optimization, and working closely with product teams to build scalable, reliable services.
    """, "Senior Software Engineer")
]

def main():
    """Test the JobMatcher implementation"""
    
    print("\n==== Testing JobMatcher Implementation ====\n")
    
    # Initialize the matcher
    print("Initializing JobMatcher...")
    matcher = JobMatcher(use_cross_encoder=False)  # Set to True to test cross-encoder reranking
    
    # Match resume to jobs
    print("\nMatching resume to jobs...\n")
    results = matcher.match_resume_to_jobs(sample_resume, [job[0] for job in sample_jobs], [job[1] for job in sample_jobs])
    
    # Print results
    print(f"\nFound {len(results)} matches, sorted by score:\n")
    print("-" * 80)
    
    for i, result in enumerate(results):
        print(f"#{i+1}: {result['job_title']} - Score: {result['final_score']:.2f}")
        print(f"  Symbolic Score: {result['symbolic_score']:.2f}, Embedding Similarity: {result['embedding_similarity']:.4f}")
        print(f"  Matched Skills ({len(result['matched_skills'])}): {', '.join(result['matched_skills'][:5])}" + 
              (f"..." if len(result['matched_skills']) > 5 else ""))
        print(f"  Missing Skills ({len(result['missing_skills'])}): {', '.join(result['missing_skills'][:5])}" + 
              (f"..." if len(result['missing_skills']) > 5 else ""))
        print(f"  Experience Match: {result['experience_match']}, New Grad Friendly: {result['new_grad_friendly']}")
        print("-" * 80)

if __name__ == "__main__":
    main()
