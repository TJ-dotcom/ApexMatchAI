from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import logging
import requests
import random
from urllib.parse import urlparse, parse_qs, urljoin
import traceback

# Get module logger
logger = logging.getLogger("job_search_app.scraper")

# List of user agents to randomize for better anonymity
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
]

def process_page(driver, url):
    """Process a job listings page with enhanced interaction methods"""
    logger.info(f"Processing {url}")
    
    # Navigate to the URL with a random delay to mimic human behavior
    driver.get(url)
    time.sleep(random.uniform(1.5, 3.0))  # Random delay to appear more human-like
    
    # Wait for page to load with different strategies based on site
    if 'linkedin.com' in url.lower():
        # LinkedIn-specific waiting strategy
        try:
            # Wait for job cards with different potential selectors
            selectors = [
                ".jobs-search-results-list",
                ".jobs-search-results__list", 
                ".job-search-card",
                ".jobs-search__results-list",
                ".artdeco-list__item"
            ]
            
            for selector in selectors:
                try:
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"LinkedIn job cards found using selector: {selector}")
                    break
                except:
                    continue
            
            logger.info("LinkedIn page loaded, implementing progressive scrolling for lazy-loaded content...")
            
            # Execute multiple slow scrolls to ensure lazy-loaded content is visible
            # This better mimics human behavior and ensures all content loads
            for i in range(4):
                scroll_height = driver.execute_script("return document.body.scrollHeight")
                for step in range(4):  # Break each scroll into multiple smaller movements
                    current_position = scroll_height * (i * 4 + step) / 16
                    driver.execute_script(f"window.scrollTo(0, {current_position});")
                    time.sleep(random.uniform(0.3, 0.7))  # Random delay between micro-scrolls
                
                # Small pause at each quarter of the page
                time.sleep(random.uniform(0.8, 1.5))
                
                # Try clicking "Show more jobs" button if present
                try:
                    show_more = driver.find_element(By.XPATH, "//button[contains(text(), 'Show more')]")
                    show_more.click()
                    time.sleep(1)
                    logger.info("Clicked 'Show more jobs' button")
                except:
                    pass
                
            # Final scroll to bottom with a bit more time to load content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2.5)
            
        except Exception as e:
            logger.warning(f"Timed out waiting for LinkedIn job cards: {str(e)}")
            # Try a more generic approach
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(3)
            
    elif 'indeed.com' in url.lower():
        # Enhanced Indeed-specific waiting strategy
        try:
            # Wait for any of multiple possible job card selectors
            selectors = [
                ".job_seen_beacon", 
                ".jobsearch-ResultsList", 
                ".mosaic-provider-jobcards", 
                ".job_component_wrapper",
                ".jobsearch-SerpJobCard", 
                ".tapItem"
            ]
            
            for selector in selectors:
                try:
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Indeed job cards found using selector: {selector}")
                    break
                except:
                    continue
            
            # Progressive scrolling for better content loading
            logger.info("Indeed page loaded, implementing progressive scrolling...")
            
            # Accept cookies if the popup appears
            try:
                cookie_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                cookie_button.click()
                logger.info("Accepted cookies on Indeed")
                time.sleep(0.5)
            except:
                pass
                
            # Close any modal that might appear
            try:
                close_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Close']")
                close_button.click()
                logger.info("Closed popup modal on Indeed")
            except:
                pass
            
            # Execute multiple slow scrolls with random pauses
            total_height = driver.execute_script("return document.body.scrollHeight")
            for i in range(5):
                scroll_position = total_height * (i + 1) / 6
                driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                time.sleep(random.uniform(0.7, 1.5))  # Random pause to mimic human reading
                
                # Try clicking "Next" or "Show more jobs" buttons if present
                try:
                    next_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Next') or contains(text(), 'Show more')]")
                    if next_button.is_displayed() and next_button.is_enabled():
                        next_button.click()
                        logger.info("Clicked navigation button to load more jobs")
                        time.sleep(2)  # Wait for new content to load
                except:
                    pass
            
            # Final scroll to ensure all content is loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2.5)
        except Exception as e:
            logger.warning(f"Timed out waiting for Indeed job cards: {str(e)}")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            
    else:
        # Enhanced generic waiting strategy with multiple detection techniques
        logger.info(f"Using advanced generic waiting strategy for {url}")
        
        # Wait for the page to load basic structure
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(random.uniform(1.0, 2.0))
        
        # Handle common cookie consent banners that might block content
        try:
            for cookie_text in ['accept cookies', 'accept all', 'i accept', 'agree', 'got it']:
                buttons = driver.find_elements(By.XPATH, f"//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{cookie_text}')]")
                for btn in buttons:
                    if btn.is_displayed():
                        btn.click()
                        logger.info(f"Accepted cookies with text: {cookie_text}")
                        time.sleep(0.5)
                        break
        except Exception as e:
            logger.debug(f"Error handling cookie consent: {e}")
        
        # Try to detect job listing elements with broader patterns
        job_found = False
        common_job_patterns = [
            "div[class*='job'], div[class*='card'], li[class*='result'], div[class*='listing']",
            "div[class*='post'], div[class*='vacancy'], div[class*='position'], div[class*='offer']",
            "article[class*='job'], article[class*='listing'], div[class*='opportunity']",
            "div.jobs, ul.jobs, div.results, ul.results, div.listings, ul.listings",
            "div[id*='job'], div[id*='result'], div[id*='listing']",
            "a[href*='job'], a[href*='career'], a[href*='position']"
        ]
        
        # Try each pattern until job elements are found
        for pattern in common_job_patterns:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, pattern)
                if elements:
                    logger.info(f"Found {len(elements)} potential job elements using pattern: {pattern}")
                    job_found = True
                    break
            except:
                continue
        
        # Progressive scrolling regardless of element detection
        logger.info("Implementing progressive scrolling for potential lazy-loaded content")
        
        # Scroll down the page in small increments to mimic human behavior
        total_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(3):  # Fewer scrolls for generic sites to save time
            scroll_position = total_height * (i + 1) / 4
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(random.uniform(0.7, 1.2))  # Random pause to mimic human reading
    
    # Ensure page has fully rendered by waiting a bit more
    time.sleep(random.uniform(0.8, 1.2))
    
    # Get the page source after all waiting and scrolling
    html_content = driver.page_source
    
    return html_content

def scrape_jobs(url: str) -> List[Dict[str, Any]]:
    """
    Scrape job listings from the given URL with advanced anonymity
    
    Args:
        url: URL of the job listing page
        
    Returns:
        List of dictionaries containing job details
    """
    logger.info(f"Starting job scraping from URL: {url}")
    driver = None
    
    try:
        # Configure enhanced Selenium options for better anonymity and reliability
        chrome_options = Options()
        
        # Use headless mode for faster scraping
        chrome_options.add_argument("--headless=new")  # New headless mode
        logger.info("Using headless mode")
        
        # Core browser settings
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Set realistic viewport
        width = random.choice([1280, 1366, 1440, 1536, 1600, 1920])
        height = random.choice([800, 864, 900, 1024, 1080])
        chrome_options.add_argument(f"--window-size={width},{height}")
        logger.info(f"Setting window size: {width}x{height}")
        
        # Enhanced anti-detection features
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Randomize user agent
        user_agent = random.choice(USER_AGENTS)
        chrome_options.add_argument(f"--user-agent={user_agent}")
        logger.info(f"Using user agent: {user_agent}")
        
        # Additional advanced anonymity options
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--disable-extensions")
        
        # Randomize language and geolocation settings to appear more organic
        languages = ["en-US,en;q=0.9", "en-GB,en;q=0.9", "en-CA,en;q=0.9", "en;q=0.9"]
        chrome_options.add_argument(f"--lang={random.choice(languages)}")
        
        # Privacy and notification settings
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # Set up the Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set timeouts appropriate for job sites
        timeout = 30
        try:
            # Set page load timeout - job sites can be slow
            driver.set_page_load_timeout(timeout)
            driver.set_script_timeout(timeout)
            logger.info(f"Set page load timeout to {timeout} seconds")
        except Exception as driver_error:
            logger.error(f"Error setting up Chrome driver: {str(driver_error)}")
            raise
                
        # Execute advanced CDP commands to bypass bot detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            // Override property detection
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
            
            // Mask WebDriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override navigator properties to make detection more difficult
            window.chrome = {
                app: {
                    isInstalled: false,
                    InstallState: {
                        DISABLED: 'disabled',
                        INSTALLED: 'installed',
                        NOT_INSTALLED: 'not_installed'
                    },
                    RunningState: {
                        CANNOT_RUN: 'cannot_run',
                        READY_TO_RUN: 'ready_to_run',
                        RUNNING: 'running'
                    }
                },
                runtime: {
                    OnInstalledReason: {
                        CHROME_UPDATE: 'chrome_update',
                        INSTALL: 'install',
                        SHARED_MODULE_UPDATE: 'shared_module_update',
                        UPDATE: 'update'
                    },
                    OnRestartRequiredReason: {
                        APP_UPDATE: 'app_update',
                        OS_UPDATE: 'os_update',
                        PERIODIC: 'periodic'
                    }
                }
            }
            """
        })
        
        # Apply final window size
        driver.set_window_size(width, height)
        
        # Determine job site type for appropriate parsing strategy
        job_site_type = "generic"
        if 'indeed.com' in url.lower():
            job_site_type = "indeed"
        elif 'linkedin.com' in url.lower():
            job_site_type = "linkedin"
        elif 'glassdoor.com' in url.lower():
            job_site_type = "glassdoor"
        elif 'monster.com' in url.lower():
            job_site_type = "monster"
        elif 'ziprecruiter.com' in url.lower():
            job_site_type = "ziprecruiter"
            
        logger.info(f"Detected job site: {job_site_type}")
        
        # Extract job title hint from URL if available for enhancing the fallback
        job_title_hint = ""
        if any(param in url for param in ["keywords=", "q=", "search=", "query=", "title="]):
            try:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                
                # Check multiple possible parameter names
                for param in ["keywords", "q", "search", "query", "title"]:
                    if param in query_params and query_params[param][0]:
                        job_title_hint = query_params[param][0].replace("+", " ").replace("%20", " ")
                        break
                        
                logger.info(f"Extracted job title hint from URL: {job_title_hint}")
            except:
                pass
        
        # Process the page with our function
        html_content = process_page(driver, url)
        
        # Parse HTML content based on site type
        primary_jobs = []
        
        if job_site_type == "indeed":
            logger.info("Using Indeed parser")
            primary_jobs = parse_indeed(html_content, url)
        elif job_site_type == "linkedin":
            logger.info("Using LinkedIn parser")
            primary_jobs = parse_linkedin(html_content, url)
        else:
            logger.info("Using generic parser")
            primary_jobs = parse_generic(html_content, url)
            
        # Enhanced validation of job data
        valid_jobs = []
        ambiguous_jobs = []
        
        for job in primary_jobs:
            # First level validation - check if essential data exists
            has_title = job.get('title') and job.get('title') != "Unknown Title"
            has_company = job.get('company') and job.get('company') != "Unknown Company"
            
            # Second level validation - check for quality/specificity
            title_quality = False
            company_quality = False
            
            if has_title:
                title = job.get('title', '')
                # Check if title seems specific enough (not just generic terms)
                generic_title_terms = ['position', 'job', 'listing', 'vacancy', 'opportunity']
                title_quality = (len(title) >= 5 and
                               not any(term == title.lower() for term in generic_title_terms) and
                               not title.startswith(('Position ', 'Job ')))
            
            if has_company:
                company = job.get('company', '')
                # Check if company seems specific enough
                generic_company_terms = ['company', 'employer', 'organization', 'recruiter']
                company_quality = (len(company) >= 3 and
                                not any(term == company.lower() for term in generic_company_terms) and
                                not company.endswith((' Employer', ' Company')))
            
            # Categorize the job based on data quality
            if has_title and has_company and title_quality and company_quality:
                # High quality job data
                valid_jobs.append(job)
            elif has_title and has_company:
                # Has required fields but quality might be questionable
                ambiguous_jobs.append(job)
            else:
                logger.warning(f"Skipping job with insufficient data: {job}")
            
        # Include ambiguous jobs only if we don't have enough valid ones
        if len(valid_jobs) < 3 and ambiguous_jobs:
            logger.info(f"Adding {len(ambiguous_jobs)} jobs with ambiguous quality to results")
            valid_jobs.extend(ambiguous_jobs)
            
        if len(valid_jobs) < len(primary_jobs):
            logger.warning(f"Filtered out {len(primary_jobs) - len(valid_jobs)} jobs with incomplete or poor quality data")
        
        # If we have jobs, return them
        if valid_jobs:
            logger.info(f"Successfully extracted {len(valid_jobs)} job listings")
            return valid_jobs
            
        # No valid jobs found, log warning and return empty list
        logger.warning(f"No jobs found at {url}")
        return []
            
    except Exception as e:
        logger.error(f"Error in scraping: {str(e)}")
        logger.error(traceback.format_exc())
        return []
        
    finally:
        if driver:
            logger.info("Closing Chrome driver")
            driver.quit()
    
def parse_indeed(html_content: str, base_url: str) -> List[Dict[str, Any]]:
    """Parse Indeed job listings"""
    logger.info("Starting Indeed parser")
    jobs = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Different card selectors for Indeed based on their evolving UI
    job_cards = []
    
    # Try several CSS selectors for job cards
    selectors = [
        ".job_seen_beacon",
        ".jobsearch-ResultsList > div", 
        ".mosaic-provider-jobcards .job_seen_beacon",
        ".tapItem",
        ".job-container",
        ".jobCard"
    ]
    
    for selector in selectors:
        cards = soup.select(selector)
        if cards:
            job_cards.extend(cards)
            logger.info(f"Found {len(cards)} job cards with selector: {selector}")
    
    # Deduplicate job cards
    seen_ids = set()
    unique_job_cards = []
    
    for card in job_cards:
        card_id = hash(card.get_text()[:50])  # Use first 50 chars of text as a hash key
        if card_id not in seen_ids:
            seen_ids.add(card_id)
            unique_job_cards.append(card)
    
    logger.info(f"Found {len(unique_job_cards)} unique job cards on Indeed")
    
    # Process each job card
    for card in unique_job_cards:
        job = {
            "title": "Unknown Title",
            "company": "Unknown Company",
            "location": "Unknown Location",
            "date_posted": "Unknown",
            "job_type": "Unknown",
            "salary": "Not specified",
            "description": "No description available",
            "url": base_url,
            "source": "Indeed"
        }
        
        # Extract job title
        title_elem = card.select_one("h2.jobTitle, h2 a, h2, .jcs-JobTitle, .jobTitle")
        if title_elem:
            job["title"] = title_elem.get_text().strip()
        
        # Extract company name
        company_elem = card.select_one(".companyName, .company, [data-testid='company-name'], .jobCompany")
        if company_elem:
            job["company"] = company_elem.get_text().strip()
        
        # Extract location
        location_elem = card.select_one(".companyLocation, .location, [data-testid='text-location']")
        if location_elem:
            job["location"] = location_elem.get_text().strip()
        
        # Extract job date
        date_elem = card.select_one(".date, .jobPostedDate, .new, .result-footer .date")
        if date_elem:
            job["date_posted"] = date_elem.get_text().strip()
        
        # Extract salary if available
        salary_elem = card.select_one(".salary-snippet-container, .salaryOnly, .metadata.salary-snippet-container")
        if salary_elem:
            job["salary"] = salary_elem.get_text().strip()
        
        # Extract job description snippet
        description_elem = card.select_one(".job-snippet, .summary, .job-snippet-container")
        if description_elem:
            job["description"] = description_elem.get_text().strip()
        
        # Extract job URL
        url_elem = card.select_one("a.jcs-JobTitle, h2 a, .title a")
        if url_elem and url_elem.get('href'):
            href = url_elem.get('href')
            if href.startswith('/'):
                job["url"] = "https://www.indeed.com" + href
            else:
                job["url"] = href
                
        # Extract job type if available
        job_type_elem = card.select_one(".jobTypes, .attribute_snippet, [data-testid='attribute_snippet']")
        if job_type_elem:
            job["job_type"] = job_type_elem.get_text().strip()
        
        # Only add jobs with at least title and company
        if job["title"] != "Unknown Title" or job["company"] != "Unknown Company":
            jobs.append(job)
    
    logger.info(f"Indeed parser extracted {len(jobs)} job listings")
    return jobs

def parse_linkedin(html_content: str, base_url: str) -> List[Dict[str, Any]]:
    """Parse LinkedIn job listings"""
    logger.info("Starting LinkedIn parser")
    jobs = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Try several CSS selectors for job cards
    job_cards = []
    selectors = [
        ".jobs-search-results__list-item",
        ".job-search-card", 
        "li.artdeco-list__item",
        ".jobs-search-results-list__list-item"
    ]
    
    for selector in selectors:
        cards = soup.select(selector)
        if cards:
            job_cards.extend(cards)
            logger.info(f"Found {len(cards)} job cards with selector: {selector}")
    
    # Deduplicate job cards
    seen_ids = set()
    unique_job_cards = []
    
    for card in job_cards:
        # Try to get LinkedIn's job ID first
        job_id = card.get('data-id', '')
        if not job_id:
            job_id = card.get('data-job-id', '')
        if not job_id:
            job_id = card.get('id', '')
            
        # If still no ID, use text content hash
        if not job_id:
            job_id = hash(card.get_text()[:50])
            
        if job_id not in seen_ids:
            seen_ids.add(job_id)
            unique_job_cards.append(card)
    
    logger.info(f"Found {len(unique_job_cards)} unique job cards on LinkedIn")
    
    # Process each job card
    for card in unique_job_cards:
        job = {
            "title": "Unknown Title",
            "company": "Unknown Company",
            "location": "Unknown Location",
            "date_posted": "Unknown",
            "job_type": "Unknown", 
            "salary": "Not specified",
            "description": "No description available",
            "url": base_url,
            "source": "LinkedIn"
        }
        
        # Extract job title
        title_elem = card.select_one(".job-card-list__title, .base-search-card__title, .job-search-card__title, h3.base-search-card__title")
        if title_elem:
            job["title"] = title_elem.get_text().strip()
        
        # Extract company name
        company_elem = card.select_one(".job-card-container__company-name, .base-search-card__subtitle, .job-search-card__subtitle-link, .base-search-card__subtitle a")
        if company_elem:
            job["company"] = company_elem.get_text().strip()
        
        # Extract location
        location_elem = card.select_one(".job-card-container__metadata-item, .job-search-card__location, .base-search-card__metadata")
        if location_elem:
            job["location"] = location_elem.get_text().strip()
        
        # Extract job date
        date_elem = card.select_one(".job-search-card__listdate, time, .job-card-container__footer-time-ago")
        if date_elem:
            date_text = date_elem.get_text().strip()
            if date_elem.get('datetime'):
                job["date_posted"] = date_elem.get('datetime')
            else:
                job["date_posted"] = date_text
        
        # Extract job description snippet
        description_elem = card.select_one(".base-card__full-link, .search-result__truncated, .base-search-card--link")
        if description_elem:
            job["description"] = description_elem.get_text().strip()
        else:
            # If no description element, try to get job criteria
            criteria_elems = card.select(".job-card-container__metadata-wrapper, .base-search-card__metadata span, .job-search-card__benefits span")
            if criteria_elems:
                job["description"] = " | ".join([e.get_text().strip() for e in criteria_elems])
        
        # Extract job URL
        url_elem = card.select_one("a.base-card__full-link, a.job-card-list__title, a.job-card-container__link")
        if url_elem and url_elem.get('href'):
            href = url_elem.get('href')
            if href.startswith('/'):
                job["url"] = "https://www.linkedin.com" + href
            else:
                job["url"] = href
        
        # Only add jobs with at least title or company
        if job["title"] != "Unknown Title" or job["company"] != "Unknown Company":
            jobs.append(job)
    
    logger.info(f"LinkedIn parser extracted {len(jobs)} job listings")
    return jobs

def parse_generic(html_content: str, base_url: str) -> List[Dict[str, Any]]:
    """Parse generic job listings with multiple heuristic approaches"""
    logger.info("Starting generic parser")
    jobs = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract from common job listing patterns
    job_containers = []
    
    # Try different selectors that are commonly used for job listings
    container_patterns = [
        "[class*='job'], [class*='jobs'], [class*='listing'], [class*='search-result']",
        "article, .card, .listing, .result, .job-card",
        "li.job, li.listing, li.result, li[id*='job'], div[id*='job']",
    ]
    
    for pattern in container_patterns:
        elements = soup.select(pattern)
        if elements:
            for element in elements:
                # Skip if it's just a header or small container
                if len(element.get_text()) > 50:  # Reasonable job listings have at least 50 chars
                    job_containers.append(element)
    
    logger.info(f"Found {len(job_containers)} potential job containers in generic parser")
    
    # If we found too many containers, they might be too general - try to be more specific
    if len(job_containers) > 30:
        refined_containers = []
        for container in job_containers:
            # Check if it has some common job listing elements
            has_title = container.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b', '.title', '[class*="title"]'])
            has_company = container.find(['[class*="company"]', '[class*="employer"]', '.org'])
            
            if has_title and has_company:
                refined_containers.append(container)
        
        if refined_containers:
            job_containers = refined_containers
            logger.info(f"Refined to {len(job_containers)} more specific job containers")
    
    # Extract job data from containers
    seen_jobs = set()  # For deduplication
    
    for container in job_containers:
        # Basic job template
        job = {
            "title": "Unknown Title",
            "company": "Unknown Company",
            "location": "Unknown Location",
            "date_posted": "Unknown",
            "job_type": "Unknown",
            "salary": "Not specified",
            "description": "No description available",
            "url": base_url,
            "source": "Generic"
        }
        
        # Extract job title - try multiple strategies
        title_elem = None
        for selector in ['h1', 'h2', 'h3', 'h4', '.title', '[class*="title"]', 'strong', 'b']:
            title_elem = container.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                job["title"] = title_elem.get_text().strip()
                break
        
        # Extract company - try multiple strategies
        company_elem = None
        for selector in ['[class*="company"]', '[class*="employer"]', '.org', '.subtitle']:
            company_elem = container.select_one(selector)
            if company_elem and company_elem.get_text().strip():
                text = company_elem.get_text().strip()
                if len(text) < 100:  # Reasonable company name length
                    job["company"] = text
                    break
        
        # Extract location
        location_elem = container.select_one('[class*="location"], [class*="address"], [class*="region"]')
        if location_elem:
            job["location"] = location_elem.get_text().strip()
        
        # Extract description
        description_elem = container.select_one('[class*="description"], [class*="summary"], [class*="excerpt"]')
        if description_elem:
            job["description"] = description_elem.get_text().strip()
        else:
            # Fallback to container text, but try to exclude the title and company
            full_text = container.get_text().strip()
            if title_elem and company_elem:
                title_text = title_elem.get_text().strip()
                company_text = company_elem.get_text().strip()
                description = full_text.replace(title_text, "", 1).replace(company_text, "", 1).strip()
                if description:
                    job["description"] = description
        
        # Extract job URL 
        url_elem = container.find('a')
        if url_elem and url_elem.get('href'):
            href = url_elem.get('href')
            if href.startswith('/'):
                # Handle relative URLs
                parsed_base = urlparse(base_url)
                job["url"] = f"{parsed_base.scheme}://{parsed_base.netloc}{href}"
            elif href.startswith('http'):
                job["url"] = href
            else:
                # Handle other relative formats
                job["url"] = urljoin(base_url, href)
        
        # Simple deduplication based on title and company
        job_key = f"{job['title']}::{job['company']}"
        if job_key not in seen_jobs and job["title"] != "Unknown Title":
            seen_jobs.add(job_key)
            jobs.append(job)
    
    logger.info(f"Generic parser extracted {len(jobs)} job listings")
    return jobs
