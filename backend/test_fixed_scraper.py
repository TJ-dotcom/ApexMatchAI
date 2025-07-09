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

def test_scraper(url: str, site_name: str):
    """Test the scraper with the given URL."""
    logger.info(f"Testing {site_name} scraper")
    
    try:
        start_time = time.time()
        jobs = scrape_jobs(url)
        end_time = time.time()
        
        logger.info(f"Found {len(jobs)} jobs in {end_time - start_time:.2f} seconds")
        
        if jobs:
            for i, job in enumerate(jobs[:3]):
                logger.info(f"  {i+1}. {job['title']} at {job['company']}")
        else:
            logger.warning("No jobs found.")
            
    except Exception as e:
        logger.error(f"Error testing scraper for {site_name}: {e}", exc_info=True)

if __name__ == "__main__":
    logger.info("=== STARTING SCRAPER TESTS ===")
    test_scraper("https://www.linkedin.com/jobs/search?keywords=software%20engineer", "LinkedIn")
    test_scraper("https://www.indeed.com/jobs?q=software+engineer", "Indeed")
    logger.info("=== TESTS COMPLETE ===")
