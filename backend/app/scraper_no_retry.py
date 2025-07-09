from typing import List, Dict, Any
from bs4 import BeautifulSoup
import time
import re
import logging
import requests
import random
from urllib.parse import urlparse, parse_qs, urljoin
import traceback
import httpx
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Get module logger
logger = logging.getLogger("job_search_app.scraper")

# Initialize UserAgent for random headers
ua = UserAgent()

# Retry decorator for HTTP requests
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_url(url: str) -> str:
    """Fetch the URL content with retry logic."""
    headers = {"User-Agent": ua.random}
    try:
        response = httpx.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except httpx.RequestError as e:
        logger.error(f"Request failed: {e}")
        raise

def scrape_jobs(url: str, proxies_list: list = None) -> list:
    """
    Scrape job listings from the given URL with advanced anonymity.
    
    Args:
        url: URL of the job listing page.
        proxies_list: Optional list of proxies to rotate through.
        
    Returns:
        List of dictionaries containing job details
    """
    logger.info(f"Starting job scraping from URL: {url}")
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        # --- Start of New Changes ---
        # 1. Use a proxy to hide your IP address
        if proxies_list:
            proxy_url = random.choice(proxies_list)
            chrome_options.add_argument(f'--proxy-server={proxy_url}')
            logger.info(f"Using proxy: {proxy_url}")
        # 2. Advanced anti-detection options
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        user_agent = ua.random
        chrome_options.add_argument(f'--user-agent={user_agent}')
        logger.info(f"Using user agent: {user_agent}")
        # --- End of New Changes ---
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(random.uniform(3, 6))  # Human-like delay
        html_content = driver.page_source
        if "linkedin.com" in url:
            logger.info("Using LinkedIn parser")
            jobs = parse_linkedin(html_content, url)
        elif "indeed.com" in url:
            logger.info("Using Indeed parser")
            jobs = parse_indeed(html_content, url)
        else:
            logger.info("Using generic parser")
            jobs = parse_generic(html_content, url)
        return jobs
    except Exception as e:
        logger.error(f"Error in scraping: {str(e)}")
        logger.error(traceback.format_exc())
        return []
    finally:
        if driver:
            driver.quit()

def parse_indeed(html_content: str, base_url: str) -> list:
    """Parse Indeed job listings with updated selectors."""
    logger.info("Starting Indeed parser with updated selectors")
    jobs = []
    soup = BeautifulSoup(html_content, 'html.parser')
    # This selector is more robust and targets the clickable card area.
    job_cards = soup.select('div.jobsearch-SerpJobCard')
    logger.info(f"Found {len(job_cards)} job cards on Indeed page")
    for card in job_cards:
        title_elem = card.select_one('h2.jobTitle > a, a.jcs-JobTitle')
        company_elem = card.select_one('[data-testid="company-name"]')
        location_elem = card.select_one('[data-testid="text-location"]')
        description_elem = card.select_one('div.job-snippet')
        title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
        company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
        location = location_elem.get_text(strip=True) if location_elem else "Unknown Location"
        description = description_elem.get_text(strip=True) if description_elem else "No description available"
        job_url = ""
        if title_elem and title_elem.get('href'):
            href = title_elem['href']
            job_url = f"https://www.indeed.com{href}" if href.startswith('/') else href
        if title != "Unknown Title":
            jobs.append({
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': job_url,
                'source': "Indeed"
            })
    if not jobs:
        logger.warning("Could not extract any jobs. The HTML structure of Indeed may have changed. Please inspect the site and update the CSS selectors.")
    return jobs

def parse_linkedin(html_content: str, base_url: str) -> List[Dict[str, Any]]:
    """Parse LinkedIn job listings with comprehensive multi-strategy approach"""
    logger.info("Starting LinkedIn parser with comprehensive extraction techniques")
    jobs = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    job_cards = soup.select(".jobs-search-results__list-item, .job-search-card")
    
    logger.info(f"Found {len(job_cards)} potential job cards on LinkedIn")
    
    for card in job_cards:
        title_elem = card.select_one("h3.base-search-card__title")
        company_elem = card.select_one("h4.base-search-card__subtitle")
        location_elem = card.select_one(".job-search-card__location")
        url_elem = card.select_one("a.base-card__full-link")

        title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
        company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
        location = location_elem.get_text(strip=True) if location_elem else "Unknown Location"
        job_url = url_elem['href'] if url_elem and url_elem.get('href') else base_url

        if title != "Unknown Title" and company != "Unknown Company":
            jobs.append({
                'title': title,
                'company': company,
                'location': location,
                'description': "Visit the job link for more details about this position.",
                'url': job_url,
                'source': "LinkedIn"
            })
    
    logger.info(f"LinkedIn parser extracted {len(jobs)} job listings")
    return jobs

def parse_generic(html_content: str, base_url: str) -> List[Dict[str, Any]]:
    """Parse generic job listings with multiple heuristic approaches"""
    logger.info("Starting generic parser")
    jobs = []
    soup = BeautifulSoup(html_content, 'html.parser')

    # Heuristics to find job elements
    job_elements = soup.select('[class*="job"], [class*="listing"], [class*="career"]')
    if not job_elements:
        job_elements = soup.find_all(['li', 'div'], text=re.compile(r'(developer|engineer|manager)', re.I))
    
    for element in job_elements:
        title = "Unknown Title"
        company = "Unknown Company"
        location = "Unknown Location"
        job_url = base_url
        
        # Try to find title
        title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
        if title_elem:
            title = title_elem.get_text(strip=True)
            
        # Try to find company
        company_elem = element.find(class_=re.compile(r'company', re.I))
        if company_elem:
            company = company_elem.get_text(strip=True)
            
        # Try to find location
        location_elem = element.find(class_=re.compile(r'location', re.I))
        if location_elem:
            location = location_elem.get_text(strip=True)
        
        # Try to find job URL
        link_elem = element.find('a', href=True)
        if link_elem and link_elem['href']:
            job_url = urljoin(base_url, link_elem['href'])

        if title != "Unknown Title" and company != "Unknown Company":
            jobs.append({
                'title': title,
                'company': company,
                'location': location,
                'description': element.get_text(strip=True)[:200] + "...",
                'url': job_url,
                'source': "Generic"
            })
            
    logger.info(f"Generic parser extracted {len(jobs)} job listings")
    return jobs
