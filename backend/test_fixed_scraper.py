"""
Robust Test Script for the New Job Scraper
"""

import logging
import sys
import os
import time
from app.scraper_no_retry import scrape_jobs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_fixed_scraper")


def test_scraper():
    """Test the scraper with fixed URLs (Moaijobs, LinkedIn, Indeed)."""
    test_cases = [
        {
            'url': "https://www.moaijobs.com/ai-engineer-jobs",
            'site_name': "Moaijobs"
        },
        {
            'url': "https://www.linkedin.com/jobs/search/?keywords=AI%20Engineer",
            'site_name': "LinkedIn"
        },
        {
            'url': "https://www.indeed.com/jobs?q=ai+engineer&l=United+States&from=searchOnDesktopSerp%2Cwhereautocomplete&vjk=2efb7713cab44a8f",
            'site_name': "Indeed (US)"
        }
    ]
    for case in test_cases:
        url = case['url']
        site_name = case['site_name']
        logger.info(f"Testing {site_name} scraper with URL: {url}")
        try:
            start_time = time.time()
            jobs = scrape_jobs(url)
            end_time = time.time()
            logger.info(f"Found {len(jobs)} jobs in {end_time - start_time:.2f} seconds for {site_name}")
            if jobs:
                for i, job in enumerate(jobs[:3]):
                    logger.info(f"  {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            else:
                logger.warning(f"No jobs found for {site_name}.")
        except Exception as e:
            logger.error(f"Error testing scraper for {site_name}: {e}", exc_info=True)

if __name__ == "__main__":
    logger.info("=== STARTING SCRAPER TEST ===")
    test_scraper()
    logger.info("=== TEST COMPLETE ===")
