"""
Test script to scrape jobs from company career pages using a CSV list.
"""
import csv
import logging
import time
import os
from app.discovery import crawl_for_career_page
from app.scraper_no_retry import scrape_jobs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test_company_scraper")

CSV_PATH = r"C:\Users\ideal\Documents\companies.csv"


def get_companies_from_csv(csv_path, limit=10):
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


def test_company_career_scraper():
    companies = get_companies_from_csv(CSV_PATH, limit=5)  # Limit for demo
    for company in companies:
        name = company["name"]
        website = company["website"]
        logger.info(f"\n=== {name} ===")
        if not website:
            logger.warning(f"No website for {name}, skipping.")
            continue
        # Try to find career page
        career_url = crawl_for_career_page(website)
        if not career_url:
            logger.warning(f"No career page found for {name} ({website})")
            continue
        logger.info(f"Career page for {name}: {career_url}")
        # Scrape jobs from career page
        try:
            start_time = time.time()
            jobs = scrape_jobs(career_url)
            end_time = time.time()
            logger.info(f"Found {len(jobs)} jobs in {end_time - start_time:.2f} seconds for {name}")
            for i, job in enumerate(jobs[:3]):
                logger.info(f"  {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            if not jobs:
                logger.warning(f"No jobs found for {name}.")
        except Exception as e:
            logger.error(f"Error scraping jobs for {name}: {e}", exc_info=True)

if __name__ == "__main__":
    logger.info("=== STARTING COMPANY CAREER SCRAPER TEST ===")
    test_company_career_scraper()
    logger.info("=== TEST COMPLETE ===")
