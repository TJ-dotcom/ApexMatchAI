# Job Search Resume Matcher - Setup and Usage Guide

## Project Overview

This application helps job seekers find the best matches for their resumes from online job listings. It uses natural language processing and semantic similarity to rank job postings based on how well they match your resume.

## How to Run the Application

### Backend Setup

1. Navigate to the backend directory and create a virtual environment:
   \`\`\`
   cd job_search_app/backend
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   # On Linux/Mac: source venv/bin/activate
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
   cd job_search_app/frontend
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

For convenience, VS Code tasks are available to run the application:

1. Press `Ctrl+Shift+P` and select "Tasks: Run Task"
2. Choose from the available tasks:
   - "Start Backend" - Runs the FastAPI server
   - "Start Frontend" - Runs the Next.js development server  
   - "Start Full App" - Runs both frontend and backend simultaneously

Alternatively, you can use the VS Code terminal and run the individual tasks using the task runner tool.

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

## Troubleshooting

### Common Issues

1. **Chrome driver issues**: If you encounter Selenium WebDriver errors, ensure Chrome is installed and up to date. The webdriver-manager should automatically handle ChromeDriver installation.

2. **spaCy model not found**: If you get a model not found error, run:
   \`\`\`
   python -m spacy download en_core_web_sm
   \`\`\`

3. **CORS errors**: The backend is configured to allow frontend connections. If you encounter CORS issues, check that both services are running on their default ports (backend: 8000, frontend: 3000).

4. **Memory issues**: Large resume files or job listing pages may cause memory issues. Consider reducing the scope of job listings or using smaller resume files.

5. **Port conflicts**: If ports 3000 or 8000 are already in use, you can modify the startup commands:
   - Frontend: `npm run dev -- -p 3001`
   - Backend: `uvicorn app.main:app --reload --port 8001`

## Environment Variables

The application currently works with default settings, but you may want to create a `.env` file in the backend directory for custom configurations:

\`\`\`
# Optional environment variables
BACKEND_HOST=localhost
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
\`\`\`

## Limitations

- The web scraper may need adjustments for specific job sites
- Processing large job listing pages may take time
- Some job sites might block automated scraping
