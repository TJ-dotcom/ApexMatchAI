"""
Test script for the no-retry scraper
"""

import logging
import sys
import os
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_no_retry_scraper")

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the new scraper without retry logic
from app.scraper_no_retry import scrape_jobs

def test_linkedin_scraper():
    """Test the LinkedIn scraper with no retry mechanism"""
    logger.info("Testing LinkedIn scraper")
    
    # URL to test
    url = "https://www.linkedin.com/jobs/search?keywords=software%20engineer&location=United%20States"
    
    try:
        # Run the scraper
        logger.info(f"Attempting to scrape: {url}")
        start_time = time.time()
        jobs = scrape_jobs(url)
        end_time = time.time()
        
        # Report results
        logger.info(f"Found {len(jobs)} jobs in {end_time - start_time:.2f} seconds")
        
        if jobs:
            # Check for unknown titles/companies
            unknown_titles = [job for job in jobs if job['title'] == "Unknown Title"]
            unknown_companies = [job for job in jobs if job['company'] == "Unknown Company"]
            
            logger.info(f"Jobs with unknown titles: {len(unknown_titles)}")
            logger.info(f"Jobs with unknown companies: {len(unknown_companies)}")
            
            # Print first 3 jobs
            logger.info("Sample jobs:")
            for i, job in enumerate(jobs[:3]):
                logger.info(f"Job {i+1}: {job['title']} at {job['company']}")
        else:
            logger.warning("No jobs found")
            
    except Exception as e:
        logger.error(f"Error testing scraper: {str(e)}", exc_info=True)
        
def test_indeed_scraper():
    """Test the Indeed scraper with no retry mechanism"""
    logger.info("Testing Indeed scraper")
    
    # URL to test
    url = "https://www.indeed.com/jobs?q=software%20engineer&l=remote"
    
    try:
        # Run the scraper
        logger.info(f"Attempting to scrape: {url}")
        start_time = time.time()
        jobs = scrape_jobs(url)
        end_time = time.time()
        
        # Report results
        logger.info(f"Found {len(jobs)} jobs in {end_time - start_time:.2f} seconds")
        
        if jobs:
            # Print first 3 jobs
            logger.info("Sample jobs:")
            for i, job in enumerate(jobs[:3]):
                logger.info(f"Job {i+1}: {job['title']} at {job['company']}")
        else:
            logger.warning("No jobs found")
            
    except Exception as e:
        logger.error(f"Error testing scraper: {str(e)}", exc_info=True)

def test_no_retry_scraper():
    """Test the no-retry scraper with a static HTML or mock"""
    logger.info("Testing no-retry scraper with static HTML")
    
    # URL to test
    url = "https://example.com/jobs"
    
    try:
        # Run the scraper
        logger.info(f"Attempting to scrape: {url}")
        jobs = scrape_jobs(url)
        
        # Check the result
        if isinstance(jobs, list):
            logger.info(f"Scraped {len(jobs)} jobs successfully")
        else:
            logger.warning("Scraped data is not in the expected list format")
            
    except Exception as e:
        logger.error(f"Error testing no-retry scraper: {str(e)}", exc_info=True)

if __name__ == "__main__":
    logger.info("Starting scraper tests without retry logic")
    test_linkedin_scraper()
    test_indeed_scraper()
    test_no_retry_scraper()
    logger.info("Tests completed")
