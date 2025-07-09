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

# Standard Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# For stealth/undetected Chrome (for anti-bot sites like Indeed)
import undetected_chromedriver as uc

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
    def run_scrape(user_agent_override=None, proxy_override=None):
        use_stealth = "indeed.com" in url.lower()
        user_agent = user_agent_override or ua.random
        local_driver = None
        headless = False if use_stealth else True  # Use headful for anti-bot
        try:
            if use_stealth:
                logger.info("Using undetected-chromedriver for anti-bot site (Indeed)")
                chrome_options = uc.ChromeOptions()
                # Use headful mode for anti-bot (no --headless)
                if headless:
                    chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                # Randomize window size
                width = random.randint(1200, 1920)
                height = random.randint(800, 1200)
                chrome_options.add_argument(f"--window-size={width},{height}")
                if proxy_override:
                    chrome_options.add_argument(f'--proxy-server={proxy_override}')
                    logger.info(f"Using proxy: {proxy_override}")
                elif proxies_list:
                    proxy_url = random.choice(proxies_list)
                    chrome_options.add_argument(f'--proxy-server={proxy_url}')
                    logger.info(f"Using proxy: {proxy_url}")
                chrome_options.add_argument(f'--user-agent={user_agent}')
                local_driver = uc.Chrome(options=chrome_options)
            else:
                chrome_options = Options()
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                if proxy_override:
                    chrome_options.add_argument(f'--proxy-server={proxy_override}')
                    logger.info(f"Using proxy: {proxy_override}")
                elif proxies_list:
                    proxy_url = random.choice(proxies_list)
                    chrome_options.add_argument(f'--proxy-server={proxy_url}')
                    logger.info(f"Using proxy: {proxy_url}")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument(f'--user-agent={user_agent}')
                logger.info(f"Using user agent: {user_agent}")
                service = Service(ChromeDriverManager().install())
                local_driver = webdriver.Chrome(service=service, options=chrome_options)
            local_driver.set_page_load_timeout(30)
            local_driver.get(url)
            # Human-like delay after page load
            time.sleep(random.uniform(2.5, 5.5))
            # Human-like scrolling
            if use_stealth:
                scroll_steps = random.randint(3, 7)
                for i in range(scroll_steps):
                    scroll_y = int((i + 1) * (local_driver.execute_script('return document.body.scrollHeight') / scroll_steps))
                    local_driver.execute_script(f"window.scrollTo(0, {scroll_y});")
                    time.sleep(random.uniform(0.8, 2.2))
            # Detect Cloudflare/CAPTCHA and pause for manual solve
            if use_stealth:
                page_source = local_driver.page_source
                if ("cf-chl-captcha-container" in page_source or "cloudflare" in page_source.lower() or "captcha" in page_source.lower()):
                    logger.warning("Cloudflare/CAPTCHA detected! Please solve it manually in the opened browser window. Press Enter in the terminal to continue after solving.")
                    input("[MANUAL ACTION REQUIRED] Solve CAPTCHA in browser, then press Enter here to continue...")
            # Wait for Indeed job cards to load if scraping Indeed
            if "indeed.com" in url.lower():
                try:
                    from selenium.webdriver.common.by import By
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    WebDriverWait(local_driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon"))
                    )
                    # Extra human-like scroll after wait
                    for _ in range(random.randint(1, 3)):
                        local_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(random.uniform(1.0, 2.5))
                except Exception as e:
                    logger.warning(f"Indeed job cards did not appear in time or scrolling failed: {e}")
                try:
                    with open("indeed_debug.html", "w", encoding="utf-8") as f:
                        f.write(local_driver.page_source)
                    local_driver.save_screenshot("indeed_debug.png")
                    logger.info("Saved Indeed debug HTML and screenshot.")
                except Exception as e:
                    logger.warning(f"Failed to save Indeed debug HTML/screenshot: {e}")
            else:
                time.sleep(random.uniform(3, 6))
            html_content = local_driver.page_source
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
        finally:
            if local_driver:
                local_driver.quit()

    try:
        # First attempt
        jobs = run_scrape()
        # If no jobs found and this is an anti-bot site, retry with new user agent/proxy
        if (not jobs or len(jobs) == 0) and ("indeed.com" in url.lower()):
            logger.info("No jobs found on first attempt, retrying with new user agent and proxy (if available)...")
            new_user_agent = ua.random
            new_proxy = None
            if proxies_list:
                new_proxy = random.choice(proxies_list)
            jobs = run_scrape(user_agent_override=new_user_agent, proxy_override=new_proxy)
        return jobs
    except Exception as e:
        logger.error(f"Error in scraping: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def parse_indeed(html_content: str, base_url: str) -> list:
    """Parse Indeed job listings with updated selectors."""
    logger.info("Starting Indeed parser with updated selectors")
    jobs = []
    soup = BeautifulSoup(html_content, 'html.parser')
    # New robust selector for Indeed job cards (2025):
    # Try to find all list items under the main job list
    # Only select job cards with a class that matches Indeed's job card pattern (e.g., 'job_seen_beacon')
    # Use the job card class from screenshot: css-3nk7qw (do not fallback to any other selector)
    # Use robust selectors as in Eben001/IndeedJobScraper
    job_cards = soup.find_all('div', class_='job_seen_beacon')
    logger.info(f"Found {len(job_cards)} job cards on Indeed page (div.job_seen_beacon)")
    for card in job_cards:
        # Job URL
        a_tag = card.find('a', {'data-jk': True})
        if a_tag and a_tag.has_attr('href'):
            job_url = urljoin('https://www.indeed.com', a_tag['href'])
        else:
            a_tag = card.find('a', class_=lambda x: x and 'JobTitle' in x)
            job_url = urljoin('https://www.indeed.com', a_tag['href']) if a_tag and a_tag.has_attr('href') else None

        # Job Title
        job_title = None
        if a_tag:
            job_title = a_tag.get_text(strip=True)
        if not job_title:
            span_title = card.find('span', id=lambda x: x and 'jobTitle-' in str(x))
            job_title = span_title.get_text(strip=True) if span_title else None

        # Company
        company_elem = card.find('span', {'data-testid': 'company-name'})
        if not company_elem:
            company_elem = card.find('span', class_=lambda x: x and 'company' in str(x).lower())
        company = company_elem.get_text(strip=True) if company_elem else None

        # Location
        location = None
        location_elem = card.find('div', {'data-testid': 'text-location'})
        if location_elem:
            span_loc = location_elem.find('span')
            location = span_loc.get_text(strip=True) if span_loc else location_elem.get_text(strip=True)
        else:
            location_elem = card.find('div', class_=lambda x: x and 'location' in str(x).lower())
            if location_elem:
                span_loc = location_elem.find('span')
                location = span_loc.get_text(strip=True) if span_loc else location_elem.get_text(strip=True)

        # Description
        desc_elem = card.find('div', class_=lambda x: x and 'job-snippet' in x)
        description = desc_elem.get_text(strip=True) if desc_elem else "See job page for details."

        # Company logo (optional)
        company_logo = None
        img_tag = card.find('img')
        if img_tag and img_tag.has_attr('src'):
            company_logo = img_tag['src']

        # Only add if title, company, and job_url are found
        if job_title and company and job_url:
            jobs.append({
                'title': job_title,
                'company': company,
                'location': location,
                'description': description,
                'url': job_url,
                'company_logo': company_logo,
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

import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

logger = logging.getLogger("job_search_app.scraper")

def parse_generic(html_content: str, base_url: str) -> List[Dict[str, Any]]:
    """
    Intelligently parse generic job listings using a scoring-based approach
    to identify job containers and extract structured data.
    """
    logger.info("Starting intelligent generic parser")
    soup = BeautifulSoup(html_content, 'html.parser')
    jobs = []
    
    # Keywords to score potential job containers
    job_keywords = [
        'apply', 'engineer', 'developer', 'manager', 'analyst', 'salary', 
        'full-time', 'part-time', 'contract', 'remote', 'location', 'company'
    ]
    
    # Find all potential containers and score them
    potential_containers = soup.find_all(['div', 'li', 'tr', 'article'])
    scored_containers = []

    for container in potential_containers:
        score = 0
        text = container.get_text(" ", strip=True).lower()
        
        # Skip containers that are too small or too large
        if not (50 < len(text) < 3000):
            continue

        # Basic scoring based on keyword presence
        for keyword in job_keywords:
            if keyword in text:
                score += 1
        
        # Boost score for elements with job-related classes or IDs
        class_str = ' '.join(container.get('class', [])).lower()
        id_str = container.get('id', '').lower()
        if any(kw in class_str for kw in ['job', 'listing', 'career', 'vacancy']):
            score += 5
        if any(kw in id_str for kw in ['job', 'listing']):
            score += 5
            
        if score > 2:  # Set a threshold to consider it a potential job
             scored_containers.append({'score': score, 'element': container})

    # Sort containers by score to prioritize the most likely candidates
    sorted_containers = sorted(scored_containers, key=lambda x: x['score'], reverse=True)
    
    # Process the top N scored containers to extract job details
    for item in sorted_containers[:25]: # Limit to the top 25 to reduce noise
        element = item['element']
        
        # --- Smarter Data Extraction ---
        title = "Unknown Title"
        company = "Unknown Company"
        location = "Remote"

        # Strategy for Title: Look for headings first, then links
        title_elem = element.find(['h1', 'h2', 'h3', 'h4']) or \
                     element.find('a', class_=re.compile(r'title', re.I))
        if title_elem:
            title = title_elem.get_text(strip=True)
        else: # Fallback to the most prominent link text
            links = element.find_all('a', href=True)
            if links:
                # Assume the link with the longest text is the title
                title = max([link.get_text(strip=True) for link in links], key=len)

        # Strategy for Company: Look for specific classes or elements near the title
        company_elem = element.find(class_=re.compile(r'company|organization|employer', re.I))
        if company_elem:
            company = company_elem.get_text(strip=True)

        # Strategy for Location: Look for location-specific classes or patterns
        location_elem = element.find(class_=re.compile(r'location|region', re.I))
        if location_elem:
            location = location_elem.get_text(strip=True)
        else: # Look for text that matches a city, state pattern
            location_match = re.search(r'\b[A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\b', element.get_text())
            if location_match:
                location = location_match.group(0)

        # Strategy for URL: Find the most relevant link
        link_elem = element.find('a', href=True)
        job_url = urljoin(base_url, link_elem['href']) if link_elem else base_url

        # --- Final Validation ---
        # Add job if we found a reasonable title and it's not a duplicate
        if title != "Unknown Title" and not any(j['title'] == title and j['company'] == company for j in jobs):
            jobs.append({
                'title': title,
                'company': company,
                'location': location,
                'description': element.get_text(" ", strip=True)[:300] + "...",
                'url': job_url,
                'source': "Generic"
            })

    logger.info(f"Intelligent generic parser extracted {len(jobs)} job listings")
    return jobs

def parse_moaijobs_listings(html_content: str, base_url: str) -> List[Dict[str, Any]]:
    """Parse MoAIjobs listings page for all job cards."""
    logger.info("Starting MoAIjobs listings parser")
    jobs = []
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find all job cards (each job card is likely a <div> or <a> with a link to the job detail page)
    # Heuristic: look for <a> tags with href starting with '/job/' and containing a job title
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/job/'):
            # Try to get job title
            title_elem = a.find('h2') or a.find('h3') or a.find('span') or a
            job_title = title_elem.get_text(strip=True) if title_elem else None
            # Try to get company and location from siblings or parent
            company = None
            location = None
            parent = a.find_parent(['div', 'li', 'section', 'article'])
            if parent:
                # Company
                company_div = parent.find('div', class_=lambda x: x and 'font-medium' in x)
                if company_div:
                    company = company_div.get_text(strip=True)
                # Location
                loc_div = parent.find('div', class_=lambda x: x and 'map-pin' in x)
                if loc_div:
                    span = loc_div.find('span')
                    if span:
                        location = span.get_text(strip=True)
            # Compose job URL
            job_url = href if href.startswith('http') else urljoin(base_url, href)
            if job_title:
                jobs.append({
                    'title': job_title,
                    'company': company,
                    'location': location,
                    'url': job_url,
                    'source': 'MoAIjobs',
                })
    logger.info(f"MoAIjobs listings parser extracted {len(jobs)} jobs.")
    return jobs
