import os
import csv
import logging
from app.discovery import find_career_page_google, crawl_for_career_page
from app.scraper_no_retry import scrape_jobs
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discovery_runner")

# --- Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

# The input file is now a CSV file
COMPANIES_FILE = r"C:\Users\ideal\Documents\companies.csv"

def main():
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        logger.error("Please set GOOGLE_API_KEY and SEARCH_ENGINE_ID in your .env file.")
        return

    try:
        with open(COMPANIES_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            companies = list(reader)
    except FileNotFoundError:
        logger.error(f"The file {COMPANIES_FILE} was not found. Please create it.")
        return

    for company_data in companies:
        company_name = company_data.get("name")
        company_url = company_data.get("domain")

        if not company_name:
            continue

        logger.info(f"--- Processing {company_name} ---")
        
        # 1. Find the career page using Google Search API
        career_page_url = find_career_page_google(company_name, GOOGLE_API_KEY, SEARCH_ENGINE_ID)
        
        # 2. If Google fails and a domain is provided, try crawling
        if not career_page_url and company_url:
            career_page_url = crawl_for_career_page(f"https://{company_url}")

        # 3. If a career page is found, scrape it
        if career_page_url:
            logger.info(f"Scraping jobs from {career_page_url}")
            jobs = scrape_jobs(career_page_url)
            
            if jobs:
                logger.info(f"Found {len(jobs)} jobs at {company_name}")
                for job in jobs:
                    print(f"  - {job['title']} at {job.get('company', company_name)}")
            else:
                logger.warning(f"No jobs found at {career_page_url}")
        else:
            logger.error(f"Could not find a career page for {company_name}")

if __name__ == "__main__":
    main()
