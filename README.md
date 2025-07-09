# Job Search Resume Matcher

Welcome! This project helps you find jobs that truly fit your resume—automatically.

## Why?
Job hunting is overwhelming. We built this tool to save you time and help you discover the best-matching jobs for your unique skills, using real natural language understanding (not just keyword matching).

## What does it do?
- Upload your resume (PDF or DOCX)
- Paste a job listings URL (e.g., LinkedIn, Indeed)
- The app scrapes, analyzes, and ranks jobs by how well they match your experience
- Download your results as a CSV

## How does it work?
We use modern NLP (spaCy, Sentence Transformers) to extract and compare skills, and a fast web UI (Next.js + React) for a smooth experience.

## Quick Start
See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for full installation and troubleshooting instructions.

## Who is this for?
Anyone who wants to cut through the noise and find jobs that actually fit—job seekers, career changers, or anyone tired of manual job searching.

## Local vs Cloud Setup

This project supports both local and cloud environments. By default, the code is configured for local development. To enable cloud integration:

1. Uncomment the relevant sections in `backend/app/vector_store.py` and `backend/app/main.py`.
2. Ensure you have the necessary GCP services (Dataflow, Vertex AI, Cloud Storage) set up.
3. Update the configuration files with your GCP credentials.

For detailed instructions, see [SETUP_GUIDE.md](./SETUP_GUIDE.md).

## Troubleshooting

### Local Environment
- Ensure MongoDB is running locally.
- Check that the backend server is accessible at http://localhost:8000.

### Cloud Environment
- Verify GCP services are active and properly configured.
- Check for network connectivity issues between your local machine and GCP.

For more troubleshooting tips, refer to [SETUP_GUIDE.md](./SETUP_GUIDE.md).

---

*Built with care by people who know the pain of job hunting. PRs and feedback welcome!*
- Selenium & BeautifulSoup for web scraping

- Pandas for CSV generation

