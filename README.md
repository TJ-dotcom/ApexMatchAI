# Job Search Resume Matcher

A web application that matches job postings from a provided URL to a user's resume using natural language processing and semantic similarity.

## Features

- Upload PDF or DOCX resumes
- Scrape job listings from various job posting websites
- Extract skills and keywords from resumes
- Compute semantic similarity between resume and job listings
- Rank job listings based on match score
- Download results as CSV

## Tech Stack

### Frontend
- React with TypeScript
- Next.js for server-side rendering
- Tailwind CSS for styling
- Axios for API requests

### Backend
- FastAPI for REST API
- PyPDF2/python-docx for resume parsing
- spaCy for natural language processing
- Sentence-Transformers for semantic embeddings
- Selenium & BeautifulSoup for web scraping
- Pandas for CSV generation

## Project Structure

\`\`\`
job_search_app/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── resume_parser.py  # extract text & keywords
│   │   ├── scraper.py        # scrape job postings
│   │   ├── matcher.py        # compute embeddings & similarity
│   │   └── utils.py          # helpers (CSV export)
│   ├── requirements.txt      # dependencies
│   └── Dockerfile            # containerization
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadForm.tsx
│   │   │   ├── ProgressIndicator.tsx
│   │   │   ├── ResultCard.tsx
│   │   │   └── DownloadLink.tsx
│   │   ├── pages/
│   │   │   └── index.tsx
│   │   └── styles/
│   ├── package.json
│   └── tailwind.config.js
└── README.md
\`\`\`

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   \`\`\`
   cd job_search_app/backend
   \`\`\`

2. Create a virtual environment:
   \`\`\`
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

3. Install dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

4. Download the spaCy model:
   \`\`\`
   python -m spacy download en_core_web_sm
   \`\`\`

5. Start the backend server:
   \`\`\`
   uvicorn app.main:app --reload
   \`\`\`

### Frontend Setup

1. Navigate to the frontend directory:
   \`\`\`
   cd job_search_app/frontend
   \`\`\`

2. Install dependencies:
   \`\`\`
   npm install
   \`\`\`

3. Start the development server:
   \`\`\`
   npm run dev
   \`\`\`

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Docker Deployment

Build and run the backend with Docker:

\`\`\`bash
cd job_search_app/backend
docker build -t job-search-backend .
docker run -p 8000:8000 job-search-backend
\`\`\`

## Usage

1. Upload your resume (PDF or DOCX format)
2. Provide a URL to job listings
3. Wait for the processing to complete
4. View the ranked job matches
5. Download the results as CSV

## License

MIT
