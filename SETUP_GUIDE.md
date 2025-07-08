# Job Search Resume Matcher - Setup and Usage Guide

## Project Overview

This application helps job seekers find the best matches for their resumes from online job listings. It uses natural language processing and semantic similarity to rank job postings based on how well they match your resume.

## How to Run the Application

### Backend Setup

1. Navigate to the backend directory and create a virtual environment:
   \`\`\`
   cd backend
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   \`\`\`

2. Install the required dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

3. Download the spaCy language model:
   \`\`\`
   python -m spacy download en_core_web_sm
   \`\`\`

4. Start the FastAPI backend server:
   \`\`\`
   uvicorn app.main:app --reload
   \`\`\`
   The API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
   \`\`\`
   cd frontend
   \`\`\`

2. Install the required dependencies:
   \`\`\`
   npm install
   \`\`\`

3. Start the development server:
   \`\`\`
   npm run dev
   \`\`\`
   The frontend will be available at http://localhost:3000

### Using VS Code Tasks

For convenience, I've created VS Code tasks to run both the frontend and backend:

1. Press `Ctrl+Shift+P` and select "Tasks: Run Task"
2. Choose "Start Full App" to run both the frontend and backend

## Using the Application

1. Upload your resume (PDF or DOCX format)
2. Enter a URL to a job listings page (e.g., LinkedIn, Indeed, Glassdoor)
3. Click "Match My Resume" and wait for the processing to complete
4. View the ranked job listings with match scores
5. Download the results as a CSV file for reference

## Features Implemented

- Resume parsing from PDF/DOCX files
- Web scraping of job listings
- Skill extraction with NLP
- Semantic matching using Sentence Transformers
- Real-time progress updates
- Ranked job results with match percentages
- CSV export of results

## Technical Details

- Backend: FastAPI with Python 3.10+
- Frontend: React with TypeScript and Next.js
- Styling: Tailwind CSS
- Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
- Web Scraping: Selenium with BeautifulSoup

## Limitations

- The web scraper may need adjustments for specific job sites
- Processing large job listing pages may take time
- Some job sites might block automated scraping
