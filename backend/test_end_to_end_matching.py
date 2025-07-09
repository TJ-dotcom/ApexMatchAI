"""
End-to-end test: Resume → Job Scraping → Matching
"""
import csv
import logging
import time
import os
from app.discovery import crawl_for_career_page
from app.scraper_no_retry import scrape_jobs
from app.resume_parser import extract_text
from app.job_matcher import JobMatcher

CSV_PATH = r"C:\Users\ideal\Documents\companies.csv"
RESUME_PATH = r"C:\Users\ideal\Downloads\Resume\Vignesh_TJ__resume.pdf"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test_end_to_end_matching")

def get_companies_from_csv(csv_path, limit=5):
    companies = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            name = row.get("Company Name")
            website = row.get("Website")
            if website and not website.startswith("http"):
                website = f"https://{website}"
            companies.append({"name": name, "website": website})
    return companies

def main():
    logger.info("=== STARTING END-TO-END MATCHING TEST ===")
    # 1. Parse resume
    logger.info(f"Parsing resume: {RESUME_PATH}")
    resume_text = extract_text(RESUME_PATH)
    logger.info(f"Extracted {len(resume_text)} characters from resume.")

    # 2. Scrape jobs from company career pages
    companies = get_companies_from_csv(CSV_PATH, limit=5)
    all_jobs = []
    for company in companies:
        name = company["name"]
        website = company["website"]
        logger.info(f"\n=== {name} ===")
        if not website:
            logger.warning(f"No website for {name}, skipping.")
            continue
        career_url = crawl_for_career_page(website)
        if not career_url:
            logger.warning(f"No career page found for {name} ({website})")
            continue
        logger.info(f"Career page for {name}: {career_url}")
        try:
            jobs = scrape_jobs(career_url)
            for job in jobs:
                job["company"] = name  # Tag with company name
                all_jobs.append(job)
            logger.info(f"Scraped {len(jobs)} jobs for {name}")
        except Exception as e:
            logger.error(f"Error scraping jobs for {name}: {e}", exc_info=True)

    if not all_jobs:
        logger.warning("No jobs scraped from any company. Exiting.")
        return

    # 3. Match resume to jobs
    logger.info(f"Matching resume to {len(all_jobs)} scraped jobs...")
    matcher = JobMatcher()
    job_texts = [job.get("description") or job.get("title") or "" for job in all_jobs]
    job_titles = [job.get("title") for job in all_jobs]
    matches = matcher.match_resume_to_jobs(resume_text, job_texts, job_titles=job_titles, limit=10)

    # 4. Output top matches
    logger.info("\n=== TOP MATCHES ===")
    for i, match in enumerate(matches):
        idx = match.get("job_index", i)
        job = all_jobs[idx] if idx < len(all_jobs) else {}
        score = match.get('score', 'N/A')
        try:
            score_str = f"{float(score):.2f}"
        except Exception:
            score_str = str(score)
        logger.info(f"{i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')} (Score: {score_str})")
        logger.info(f"    URL: {job.get('url', 'N/A')}")

    logger.info("=== END-TO-END TEST COMPLETE ===")

if __name__ == "__main__":
    main()
