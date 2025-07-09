"""
Test script to verify the improved scraper functionality.
This script will attempt to scrape jobs from LinkedIn with our enhanced scraping mechanisms.
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
logger = logging.getLogger("test_improved_scraper")

# Add app directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the scraper
from app.scraper import scrape_jobs

def test_linkedin_scraper():
    """Test the LinkedIn scraper with enhanced retry mechanisms"""
    logger.info("Testing LinkedIn scraper with enhanced retry mechanisms")
    
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
        
        # Check for any 'Unknown Title' or 'Unknown Company'
        unknown_titles = [job for job in jobs if job['title'] == "Unknown Title"]
        unknown_companies = [job for job in jobs if job['company'] == "Unknown Company"]
        
        logger.info(f"Jobs with 'Unknown Title': {len(unknown_titles)}")
        logger.info(f"Jobs with 'Unknown Company': {len(unknown_companies)}")
        
        # Check for title/company quality
        generic_titles = [job for job in jobs if job['title'].lower() in ["position", "job", "professional position"]]
        logger.info(f"Jobs with generic titles: {len(generic_titles)}")
        
        # Calculate quality metrics
        quality_score = 100 - ((len(unknown_titles) + len(unknown_companies) + len(generic_titles)) * 100 / len(jobs) if jobs else 0)
        logger.info(f"Overall job data quality score: {quality_score:.1f}%")
        
        # Print first 5 jobs as a sample
        logger.info("Sample of scraped jobs:")
        for i, job in enumerate(jobs[:5]):
            logger.info(f"{i+1}. {job['title']} at {job['company']} - URL: {job.get('url', 'No URL')}")
            
        return jobs
        
    except Exception as e:
        logger.error(f"Error testing scraper: {e}", exc_info=True)
        return []


def test_indeed_scraper():
    """Test the Indeed scraper with enhanced retry mechanisms"""
    logger.info("Testing Indeed scraper with enhanced retry mechanisms")
    
    # URL to test
    url = "https://www.indeed.com/jobs?q=software+engineer&l=Remote"
    
    try:
        # Run the scraper
        logger.info(f"Attempting to scrape: {url}")
        start_time = time.time()
        jobs = scrape_jobs(url)
        end_time = time.time()
        
        # Report results
        logger.info(f"Found {len(jobs)} jobs in {end_time - start_time:.2f} seconds")
        
        # Check for any 'Unknown Title' or 'Unknown Company'
        unknown_titles = [job for job in jobs if job['title'] == "Unknown Title"]
        unknown_companies = [job for job in jobs if job['company'] == "Unknown Company"]
        
        logger.info(f"Jobs with 'Unknown Title': {len(unknown_titles)}")
        logger.info(f"Jobs with 'Unknown Company': {len(unknown_companies)}")
        
        # Print first 5 jobs as a sample
        logger.info("Sample of scraped jobs:")
        for i, job in enumerate(jobs[:5]):
            logger.info(f"{i+1}. {job['title']} at {job['company']} - URL: {job.get('url', 'No URL')}")
            
        return jobs
        
    except Exception as e:
        logger.error(f"Error testing scraper: {e}", exc_info=True)
        return []
        
def run_comprehensive_tests():
    """Run comprehensive tests on multiple job sites"""
    logger.info("Running comprehensive scraper tests")
    
    all_results = {}
    
    # Test LinkedIn
    logger.info("===== LINKEDIN TEST =====")
    linkedin_jobs = test_linkedin_scraper()
    all_results["LinkedIn"] = len(linkedin_jobs)
    
    # Pause between tests
    time.sleep(5)
    
    # Test Indeed
    logger.info("===== INDEED TEST =====")
    indeed_jobs = test_indeed_scraper()
    all_results["Indeed"] = len(indeed_jobs)
    
    # Print summary of all results
    logger.info("===== TEST SUMMARY =====")
    for site, job_count in all_results.items():
        logger.info(f"{site}: {job_count} jobs scraped")
    
    total_jobs = sum(all_results.values())
    logger.info(f"Total jobs scraped across all sites: {total_jobs}")
    logger.info("Tests completed")

def test_improved_scraper_quality():
    """Test the scraper's job data quality with known static HTML or mock"""
    logger.info("Testing scraper job data quality")
    
    # Use a known static HTML or mock
    url = "https://example.com/jobs"
    jobs = scrape_jobs(url)
    
    for job in jobs:
        assert "title" in job and job["title"], "Job title is missing or empty"
        assert "company" in job and job["company"], "Company name is missing or empty"
        assert "description" in job, "Job description is missing"
        # Check for unknown titles/companies
        assert not job["title"].lower().startswith("unknown"), f"Job title should not be unknown: {job['title']}"
        assert not job["company"].lower().startswith("unknown"), f"Company name should not be unknown: {job['company']}"

if __name__ == "__main__":
    # Uncomment the test you want to run:
    
    # Test just LinkedIn
    test_linkedin_scraper()
    
    # Test just Indeed
    # test_indeed_scraper()
    
    # Test multiple sites
    # run_comprehensive_tests()

    # Test improved scraper quality
    # test_improved_scraper_quality()
