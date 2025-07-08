"""
Test script for the improved job scraper using the fixed module.
"""

import logging
import sys
import os
import time
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_fixed_scraper")

# Import the fixed scraper module dynamically
spec = importlib.util.spec_from_file_location(
    "scraper", 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "scraper.py.fixed")
)
scraper_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper_module)

def test_linkedin_scraper():
    """Test the LinkedIn scraper with enhanced retry mechanisms"""
    logger.info("Testing LinkedIn scraper with enhanced retry mechanisms")
    
    # URL to test
    url = "https://www.linkedin.com/jobs/search?keywords=software%20engineer&location=United%20States"
    
    try:
        # Run the scraper
        logger.info(f"Attempting to scrape: {url}")
        start_time = time.time()
        jobs = scraper_module.scrape_jobs(url)
        end_time = time.time()
        
        # Report results
        logger.info(f"Found {len(jobs)} jobs in {end_time - start_time:.2f} seconds")
        
        # Print summary
        if jobs:
            # Check for unknown titles/companies
            unknown_titles = [job for job in jobs if job['title'] == "Unknown Title"]
            unknown_companies = [job for job in jobs if job['company'] == "Unknown Company"]
            
            logger.info(f"Jobs with 'Unknown Title': {len(unknown_titles)}")
            logger.info(f"Jobs with 'Unknown Company': {len(unknown_companies)}")
            
            # Print first 5 jobs as a sample
            logger.info("Sample of scraped jobs:")
            for i, job in enumerate(jobs[:5]):
                logger.info(f"{i+1}. {job['title']} at {job['company']} - URL: {job.get('url', 'No URL')}")
        else:
            logger.error("No jobs found")
            
        return jobs
        
    except Exception as e:
        logger.error(f"Error testing scraper: {e}", exc_info=True)
        return []

if __name__ == "__main__":
    logger.info("=== STARTING SCRAPER TEST WITH FIXED MODULE ===")
    test_linkedin_scraper()
    logger.info("=== TEST COMPLETE ===")
