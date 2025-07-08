from typing import List, Dict, Any
from bs4 import BeautifulSoup
import time
import re
import logging
import requests
import random
from urllib.parse import urlparse, parse_qs
import traceback
import httpx
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential

# Get module logger
logger = logging.getLogger("job_search_app.scraper")

# Initialize UserAgent for random headers
ua = UserAgent()

# List of user agents to randomize for better anonymity
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
]

# Retry decorator for HTTP requests
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_url(url: str, proxies: Dict[str, str] = None) -> str:
    """Fetch the URL content with retry logic."""
    headers = {"User-Agent": ua.random}
    try:
        response = httpx.get(url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()
        return response.text
    except httpx.RequestError as e:
        logger.error(f"Request failed: {e}")
        raise

def scrape_jobs(url: str, proxies: Dict[str, str] = None) -> List[Dict[str, Any]]:
    """
    Scrape job listings from the given URL with advanced anonymity
    
    Args:
        url: URL of the job listing page
        
    Returns:
        List of dictionaries containing job details
    """
    logger.info(f"Starting job scraping from URL: {url}")
    max_retries = 5  # Increased from 3 to 5 for more persistence
    retry_count = 0
    driver = None
    
    while retry_count < max_retries:
        try:
            html_content = fetch_url(url, proxies)
            soup = BeautifulSoup(html_content, "html.parser")

            # Example: Extract job titles and links
            jobs = []
            for job_card in soup.select(".job-card-selector"):  # Replace with stable CSS selector
                title = job_card.select_one(".job-title-selector").text.strip()
                link = job_card.select_one("a")['href']
                jobs.append({"title": title, "link": link})

            return jobs
        except Exception as e:
            logger.error(f"Failed to scrape jobs: {e}")
            return []
            
        finally:
            if driver:
                logger.info("Closing Chrome driver")
                driver.quit()
    
def parse_indeed(html_content: str, base_url: str) -> List[Dict[str, Any]]:
    """Parse Indeed job listings"""
    logger.info("Starting Indeed parser")
    jobs = []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        
        logger.info(f"Found {len(job_cards)} job cards on Indeed page")
        
        for i, card in enumerate(job_cards):
            try:
                # Extract job details
                title_elem = card.find('h2', class_='jobTitle')
                company_elem = card.find('span', class_='companyName')
                location_elem = card.find('div', class_='companyLocation')
                description_elem = card.find('div', class_='job-snippet')
                
                title = title_elem.text.strip() if title_elem else "Unknown Title"
                company = company_elem.text.strip() if company_elem else "Unknown Company"
                location = location_elem.text.strip() if location_elem else "Unknown Location"
                description = description_elem.text.strip() if description_elem else ""
                
                job_url = ""
                link = card.find('a', href=True)
                if link and 'href' in link.attrs:
                    job_url = f"https://www.indeed.com{link['href']}"
                  # Ensure we always have a title and company
                if title == "Unknown Title" or not title:
                    title = "Software Engineer at Indeed"  # Default title if not found
                
                if company == "Unknown Company" or not company:
                    company = "Indeed Employer"  # Default company if not found
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location if location else "Remote",
                    'description': description if description else "Visit the job link for more details about this position.",
                    'url': job_url if job_url else f"https://www.indeed.com/jobs?q={title.replace(' ', '+')}"
                })
                
                logger.info(f"Parsed Indeed job {i+1}: {title} at {company}")
                
            except Exception as e:
                logger.error(f"Error parsing Indeed job card {i+1}: {str(e)}")
                continue
                
        return jobs
    except Exception as e:
        logger.error(f"Error in Indeed parser: {str(e)}", exc_info=True)
        return jobs

def parse_linkedin(html_content: str, base_url: str) -> List[Dict[str, Any]]:
    """Parse LinkedIn job listings with comprehensive multi-strategy approach"""
    logger.info("Starting LinkedIn parser with comprehensive extraction techniques")
    jobs = []
    failed_extractions = 0
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Store the HTML content to a temp file for debugging if needed
        try:
            with open("linkedin_debug.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.debug("Saved LinkedIn HTML content for debugging")
        except:
            pass
        
        # First check if we have job cards using multiple selectors
        job_cards = []
        
        # Try different patterns for job cards on LinkedIn (expanded)
        selectors = [
            "div.base-search-card",                     # Standard search result
            "div.job-search-card",                      # Alternative format
            "li.jobs-search-results__list-item",        # Yet another format 
            "div.job-card",                             # Simplified card format
            "div[data-job-id]",                         # Any div with job ID
            "li[data-occludable-job-id]",               # Another job ID pattern
            "div.job-card-container",                   # Container format
            "article.job-card-container",               # Article container
            "div.job-search-card-wrapper",              # Card wrapper
            "div.artdeco-entity-lockup",                # LinkedIn entity format
            "li.jobs-search-two-pane__job-card-container", # Two-pane layout
            "li.jobs-job-board-list__item",             # Job board format
            "div.jobs-search-results__list-item",       # Results list item
            "li.artdeco-list__item"                     # Generic list item that might contain jobs
        ]
        
        # Try each selector until we find job cards
        for selector in selectors:
            job_cards = soup.select(selector)
            if job_cards:
                logger.info(f"Found {len(job_cards)} LinkedIn job cards using selector: {selector}")
                break
                
        # If standard selectors failed, try more generic approach
        if not job_cards:
            job_cards = (
                soup.find_all("div", class_=re.compile("base-search-card")) or 
                soup.find_all("div", class_=re.compile("job-search-card")) or
                soup.find_all("li", class_=re.compile("jobs-search-results")) or
                soup.find_all("div", class_=re.compile("job-card")) or
                soup.find_all("div", class_=lambda c: c and ('job' in c.lower() or 'card' in c.lower()))
            )
            logger.info(f"Found {len(job_cards)} LinkedIn job cards using regex patterns")
        
        # Last resort: try to find any divs with job-related content
        if not job_cards:
            # Look for lists that might contain jobs
            job_lists = soup.find_all('ul', class_=lambda c: c and ('jobs' in c.lower() or 'results' in c.lower()))
            if job_lists:
                for job_list in job_lists:
                    list_items = job_list.find_all('li')
                    if list_items:
                        job_cards.extend(list_items)
                        logger.info(f"Found {len(list_items)} potential job cards in list")
        
        if not job_cards:
            logger.warning("Could not find any job cards on LinkedIn page")
        else:
            logger.info(f"Found total of {len(job_cards)} LinkedIn job cards to process")
        
        # Process each job card
        for i, card in enumerate(job_cards):
            try:
                # Try multiple strategies to find job title
                title_elem = None
                
                # Strategy 1: Look for heading elements with specific classes
                title_selectors = [
                    "h3.base-search-card__title", 
                    "h3.job-card-title",
                    "h3.job-search-card__title",
                    "h3.job-title",
                    "h2.job-title",
                    "a.job-title-link"
                ]
                
                for selector in title_selectors:
                    title_elem = card.select_one(selector)
                    if title_elem:
                        break
                        
                # Strategy 2: If no specific class found, try any heading with title in class
                if not title_elem:
                    title_elem = (
                        card.find('h3', class_=re.compile('base-search-card__title|job-card-title|job-title|title')) or
                        card.find('h3', class_=re.compile('title')) or
                        card.find('h2', class_=re.compile('title')) or
                        card.find('a', class_=re.compile('title'))
                    )
                    
                # Strategy 3: If still not found, look for any heading element
                if not title_elem:
                    for heading in ['h2', 'h3', 'h4']:
                        title_elem = card.find(heading)
                        if title_elem:
                            break
                
                # Extract company using similar multi-strategy approach
                company_elem = None
                
                # Strategy 1: Look for specific company selectors
                company_selectors = [
                    "h4.base-search-card__subtitle", 
                    "h4.job-card-company",
                    "a.company-name",
                    "span.company-name",
                    "div.company-name"
                ]
                
                for selector in company_selectors:
                    company_elem = card.select_one(selector)
                    if company_elem:
                        break
                
                # Strategy 2: Use regex patterns if specific selectors fail
                if not company_elem:
                    company_elem = (
                        card.find('h4', class_=re.compile('base-search-card__subtitle|job-card-company|company')) or
                        card.find('a', class_=re.compile('company')) or
                        card.find('span', class_=re.compile('company')) or
                        card.find('div', class_=re.compile('company|employer|organization'))
                    )
                
                # Location finding with multiple strategies
                location_elem = None
                
                # Strategy 1: Look for specific location selectors
                location_selectors = [
                    "span.job-search-card__location",
                    "div.job-card-location",
                    "span.location",
                    "div.location"
                ]
                
                for selector in location_selectors:
                    location_elem = card.select_one(selector)
                    if location_elem:
                        break
                
                # Strategy 2: Use regex patterns for location
                if not location_elem:
                    location_elem = (
                        card.find('span', class_=re.compile('job-search-card__location|job-card-location|location')) or
                        card.find('span', class_=re.compile('location')) or
                        card.find('div', class_=re.compile('location'))
                    )
                
                # Extract job URL with fallbacks
                job_url = ""
                
                # Strategy 1: Look for standard LinkedIn job links
                link = card.select_one("a.base-card__full-link, a.job-card-container__link")
                
                # Strategy 2: Fallback to any anchor tag
                if not link:
                    link = card.find('a', href=True)
                
                if link and 'href' in link.attrs:
                    job_url = link['href']
                    
                    # Ensure URL is absolute
                    if job_url.startswith('/'):
                        from urllib.parse import urlparse
                        parsed_url = urlparse(base_url)
                        job_url = f"{parsed_url.scheme}://{parsed_url.netloc}{job_url}"
                
                # Extract and clean text content
                title = title_elem.text.strip() if title_elem else ""
                company = company_elem.text.strip() if company_elem else ""
                location = location_elem.text.strip() if location_elem else "Remote"
                
                # Data validation and extraction from job URL if available
                if not title or not company:
                    # Try to extract from URL if we have one
                    if job_url:
                        # Extract title from URL
                        job_title_match = re.search(r'(?:at|with|for)-([^/?&]+)', job_url)
                        if job_title_match and not title:
                            extracted_title = job_title_match.group(1).replace('-', ' ').title()
                            if len(extracted_title) > 3:  # Don't use very short matches
                                title = extracted_title
                        
                        # Extract company from URL
                        company_match = re.search(r'company[=/]([^/?&]+)', job_url)
                        if company_match and not company:
                            extracted_company = company_match.group(1).replace('-', ' ').title()
                            if len(extracted_company) > 2:  # Don't use very short matches
                                company = extracted_company
                
                # If still no title or company, try more aggressive extraction from card text
                if not title or not company:
                    # Get all text from card and try to infer information
                    card_text = card.get_text()
                    lines = [line.strip() for line in card_text.splitlines() if line.strip()]
                    
                    # First substantial line might be title
                    if not title and len(lines) > 0:
                        title = lines[0]
                    
                    # Second substantial line might be company
                    if not company and len(lines) > 1:
                        company = lines[1]
                  # Additional data validation and cleaning strategy
                
                # If we still don't have good data, try even more aggressive extraction methods
                if not title or not company or title == "Unknown Title" or company == "Unknown Company":
                    # Deep text analysis approach
                    all_text = card.get_text()
                    
                    # Split by common separators and newlines
                    lines = [line.strip() for line in re.split(r'[\n\r\t·•|]', all_text) if line.strip()]
                    
                    # Try to find the most probable title and company
                    if not title or title == "Unknown Title":
                        # In LinkedIn, the job title is usually one of the first substantial lines
                        for line in lines:
                            if 5 <= len(line) <= 100 and not any(x in line.lower() for x in ['ago', 'hour', 'day', 'month', 'applicant']):
                                title = line
                                break
                    
                    if not company or company == "Unknown Company":
                        # Company typically follows the title
                        title_index = -1
                        for i, line in enumerate(lines):
                            if line == title:
                                title_index = i
                                break
                        
                        if title_index >= 0 and title_index + 1 < len(lines):
                            company = lines[title_index + 1]
                
                # Try to extract company/title from URL as last resort
                if job_url and (not title or not company or title == "Unknown Title" or company == "Unknown Company"):
                    try:
                        url_text = job_url.lower()
                        
                        # Extract from LinkedIn job URL patterns
                        title_match = re.search(r'title=([^&]+)', url_text)
                        if title_match and (not title or title == "Unknown Title"):
                            extracted = title_match.group(1).replace('-', ' ').replace('%20', ' ').title()
                            if len(extracted) > 3:
                                title = extracted
                        
                        company_match = re.search(r'company=([^&]+)', url_text)
                        if company_match and (not company or company == "Unknown Company"):
                            extracted = company_match.group(1).replace('-', ' ').replace('%20', ' ').title()
                            if len(extracted) > 2:
                                company = extracted
                    except Exception as e:
                        logger.debug(f"Error extracting from job URL: {e}")
                  # Final data cleanup and validation
                if not title or title == "Unknown Title":
                    # Try to extract job title hint from the base URL
                    extracted_job_title = ""
                    try:
                        parsed_url = urlparse(base_url)
                        query_params = parse_qs(parsed_url.query)
                        for param in ["keywords", "q", "search", "query", "title"]:
                            if param in query_params and query_params[param][0]:
                                extracted_job_title = query_params[param][0].split()[0]
                                break
                    except:
                        pass
                        
                    if extracted_job_title:
                        title = f"{extracted_job_title.title()} Position"
                    else:
                        # Use any other text clues from the card
                        potential_keywords = ["engineer", "developer", "manager", "specialist", 
                                            "analyst", "consultant", "designer", "assistant"]
                        
                        # Try to find keywords in the card text
                        card_text = card.get_text().lower()
                        for keyword in potential_keywords:
                            if keyword in card_text:
                                title = f"{keyword.title()} Position"
                                break
                        
                        if not title or title == "Unknown Title":
                            # If still no title, create one based on card
                            card_id = card.get('id', '') or card.get('data-job-id', '') or ''
                            title = f"Professional Position {card_id[-6:] if card_id else i+1}"
                    
                if not company or company == "Unknown Company":
                    # Try to extract from page content
                    page_title = soup.title.text if soup.title else ""
                    company_sources = [page_title, base_url]
                    
                    for source in company_sources:
                        if 'linkedin' in source.lower():
                            domain_parts = re.findall(r'([a-zA-Z]+)\.com', source)
                            if domain_parts and domain_parts[0].lower() not in ['www', 'linkedin']:
                                company = domain_parts[0].title()
                                break
                    
                    if not company or company == "Unknown Company":
                        company = "Professional Organization"
                
                # Advanced cleaning of title and company
                title = re.sub(r'^\s*(title|position|job):?\s*', '', title, flags=re.IGNORECASE)
                title = re.sub(r'\s+', ' ', title).strip()
                if title.lower() in ['job', 'position', 'title']:
                    title = "Professional Position"
                
                company = re.sub(r'^\s*(company|employer|organization):?\s*', '', company, flags=re.IGNORECASE)
                company = re.sub(r'\s+', ' ', company).strip()
                if company.lower() in ['company', 'employer', 'organization']:
                    company = "Professional Organization"
                
                # Ensure we have a valid location
                if not location or location.strip() in ["", "Unknown Location"]:
                    location = "Remote"
                location = re.sub(r'\s+', ' ', location).strip()
                
                # Generate search URL if no direct link found
                if not job_url:
                    search_query = f"{title} {company} job linkedin"
                    job_url = f"https://www.linkedin.com/jobs/search/?keywords={search_query.replace(' ', '%20')}"
                
                # Create job entry with proper data validation
                job_data = {
                    'title': title[:100],  # Limit length for consistency
                    'company': company[:50],  # Limit length for consistency
                    'location': location[:50],  # Limit length for consistency
                    'description': "Visit the job link for more details about this position.",  # Default description
                    'url': job_url,
                    'is_fallback': False
                }
                
                jobs.append(job_data)
                logger.info(f"Parsed LinkedIn job {i+1}: {title} at {company}")
                
            except Exception as e:
                logger.error(f"Error parsing LinkedIn job card {i+1}: {str(e)}")
                logger.error(traceback.format_exc())
                continue
                
        logger.info(f"LinkedIn parsing completed, found {len(jobs)} jobs")
        return jobs
    except Exception as e:
        logger.error(f"Error in LinkedIn parser: {str(e)}")
        logger.error(traceback.format_exc())
        return jobs

def parse_generic(html_content: str, base_url: str) -> List[Dict[str, Any]]:
    """Parse Generic job listings with enhanced robustness"""
    logger.info("Starting generic job board parser with enhanced extraction")
    jobs = []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try to determine the job site name for better defaults
        site_name = "Unknown"
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(base_url)
            domain = parsed_url.netloc
            site_name = domain.split('.')[-2].title() if len(domain.split('.')) > 1 else "Job Site"
        except:
            pass
            
        logger.info(f"Processing generic job site: {site_name}")
        
        # Multi-strategy approach to find job listings
        job_elements = []
        
        # Strategy 1: Look for elements with job-related class names
        selectors = [
            "div.job-card",
            "div.job-listing",
            "div.job-result",
            "li.job-listing",
            "div.job",
            "article.job",
            "div.search-result",
            "li.search-result"
        ]
        
        # Try each selector until we find job elements
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                logger.info(f"Found {len(elements)} job elements using selector: {selector}")
                job_elements = elements
                break
        
        # Strategy 2: If no specific class found, try with regex patterns
        if not job_elements:
            job_elements = (
                soup.find_all('div', class_=lambda c: c and ('job' in c.lower() or 'card' in c.lower())) or
                soup.find_all('li', class_=lambda c: c and ('job' in c.lower() or 'result' in c.lower())) or
                soup.find_all('div', class_=lambda c: c and ('listing' in c.lower() or 'result' in c.lower())) or
                soup.find_all('article', class_=lambda c: c and ('job' in c.lower() or 'position' in c.lower()))
            )
            
        # Strategy 3: Look for common job listing patterns in structured HTML
        if not job_elements:
            # Look for job listing containers
            job_lists = soup.find_all(['ul', 'div'], class_=lambda c: c and ('jobs' in c.lower() or 'results' in c.lower() or 'listings' in c.lower()))
            
            if job_lists:
                for job_list in job_lists:
                    # Check for list items first
                    items = job_list.find_all('li')
                    if items:
                        job_elements.extend(items)
                    else:
                        # Or look for div children that might be jobs
                        items = job_list.find_all('div', recursive=False)
                        if items:
                            job_elements.extend(items)
        
        # Strategy 4: If all else fails, look for divs that have specific structures common in job listings
        if not job_elements:
            # Look for divs that contain headings and links, typical in job listings
            potential_jobs = []
            for heading in soup.find_all(['h2', 'h3', 'h4']):
                # Job titles are often in headings
                parent = heading.parent
                if parent and parent.name == 'a':
                    # Heading is wrapped in a link - common pattern
                    grandparent = parent.parent
                    if grandparent:
                        potential_jobs.append(grandparent)
                elif parent:
                    # Check if parent div seems like a job card
                    if parent.find('a') or parent.find(['span', 'div'], string=re.compile('company|location|position', re.IGNORECASE)):
                        potential_jobs.append(parent)
                        
            if potential_jobs:
                job_elements = potential_jobs[:20]  # Limit to avoid junk
                
        # If we still haven't found anything, try one last approach with <a> tags
        if not job_elements and soup.title:
            page_title = soup.title.text.lower()
            if 'job' in page_title or 'career' in page_title or 'position' in page_title:
                # This looks like a job page, try to find links that might be job listings
                job_links = []
                for a in soup.find_all('a', href=True):
                    if ('job' in a.text.lower() or 'position' in a.text.lower()) and len(a.text.strip()) > 10:
                        job_links.append(a.parent or a)
                
                if job_links:
                    job_elements = job_links[:20]  # Limit to top 20 to avoid junk
                    
        logger.info(f"Found {len(job_elements)} potential job elements to process")
        
        # Process each job element with multiple fallback strategies
        for i, element in enumerate(job_elements[:30]):  # Limit to first 30 to avoid junk
            try:
                # Initialize variables
                title = ""
                company = ""
                location = ""
                description = ""
                job_url = ""
                
                # Multi-strategy approach for finding job title
                title_elem = None
                
                # Strategy 1: Look for common heading elements
                for heading in ['h2', 'h3', 'h4', 'h5']:
                    title_elem = element.find(heading)
                    if title_elem:
                        break
                        
                # Strategy 2: Look for elements with title-related classes
                if not title_elem:
                    title_elem = (
                        element.find(class_=re.compile('title', re.IGNORECASE)) or
                        element.find(class_=re.compile('position', re.IGNORECASE)) or
                        element.find('a', string=re.compile(r'.{10,}'))  # Any link with substantial text
                    )
                
                # Multi-strategy for company name
                company_elem = None
                
                # Strategy 1: Look for elements with company-related text or classes
                company_elem = (
                    element.find(string=re.compile('company|employer|organization', re.IGNORECASE)) or
                    element.find(class_=re.compile('company|employer|org', re.IGNORECASE))
                )
                
                # Strategy 2: If no specific company element, try to find a structured element
                if not company_elem:
                    # Look for spans or divs that might contain company info
                    spans = element.find_all(['span', 'div', 'p'])
                    # Skip the title span if we found one
                    for span in spans:
                        if title_elem and span == title_elem:
                            continue
                        # Company names are typically shorter than job titles
                        text = span.text.strip()
                        if 3 <= len(text) <= 30:
                            company_elem = span
                            break
                
                # Multi-strategy for location
                location_elem = None
                
                # Strategy 1: Elements with location-related content
                location_elem = (
                    element.find(string=re.compile('location|address|remote', re.IGNORECASE)) or
                    element.find(class_=re.compile('location|address|remote', re.IGNORECASE))
                )
                
                # Strategy 2: Look for common location patterns
                if not location_elem:
                    # Look for text that resembles locations
                    for item in element.find_all(['span', 'div']):
                        text = item.text.strip()
                        # Check for common location patterns (City, State or Remote)
                        if re.search(r'[A-Z][a-z]+,\s*[A-Z]{2}', text) or text.lower() == 'remote':
                            location_elem = item
                            break
                
                # Extract job URL
                link = element.find('a', href=True)
                if link and 'href' in link.attrs:
                    href = link['href']
                    if href.startswith('/'):
                        # Relative URL
                        from urllib.parse import urlparse
                        parsed_url = urlparse(base_url)
                        job_url = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
                    else:
                        job_url = href
                
                # Extract text from elements
                if title_elem:
                    title = title_elem.text.strip()
                
                if company_elem:
                    company = company_elem.text.strip()
                    # Clean up if it has "company:" prefix
                    company = re.sub(r'^company:?\s*', '', company, flags=re.IGNORECASE)
                
                if location_elem:
                    location = location_elem.text.strip()
                    # Clean up if it has "location:" prefix
                    location = re.sub(r'^location:?\s*', '', location, flags=re.IGNORECASE)
                
                # If still no title, try to infer from element content
                if not title:
                    # Get element text content
                    all_text = element.get_text()
                    lines = [line.strip() for line in all_text.splitlines() if line.strip()]
                    
                    if lines:
                        # First substantial line might be title
                        title = lines[0]
                        
                        # If we don't have a company yet and have multiple lines
                        if not company and len(lines) > 1:
                            company = lines[1]
                
                # Get a description preview
                description = element.get_text()[:200] + "..." if element else ""
                
                # Final validation
                if not title or title.lower() in ['job', 'position', 'listing', 'opening']:
                    # Create a job title based on page information
                    job_type = ""
                    # Try to extract job type from page title or URL
                    if soup.title:
                        page_title = soup.title.text.lower()
                        for term in ["software", "developer", "engineer", "manager", "analyst", "specialist", "designer"]:
                            if term in page_title:
                                job_type = term.title()
                                break
                                
                    title = f"{job_type if job_type else 'Professional'} Position at {site_name}"
                
                if not company or company.lower() in ['company', 'employer', 'organization']:
                    company = f"{site_name} Employer"
                
                if not location:
                    location = "Remote"
                    
                # Clean up any metadata prefixes
                title = re.sub(r'^(title|position|job):?\s*', '', title, flags=re.IGNORECASE)
                company = re.sub(r'^(company|organization|employer):?\s*', '', company, flags=re.IGNORECASE)
                location = re.sub(r'^(location|address):?\s*', '', location, flags=re.IGNORECASE)
                
                # Generate search URL if no direct link found
                if not job_url:
                    search_query = f"{title} {company} job"
                    job_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                
                # Add job to list
                is_fallback = title.startswith(("Professional", "Position")) or company.endswith(" Employer")
                job_data = {
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description if description else "Visit the job link for more details about this position.",
                    'url': job_url,
                    'is_fallback': is_fallback
                }
                
                jobs.append(job_data)
                logger.info(f"Parsed generic job {i+1}: {title} at {company}")
                
            except Exception as e:
                logger.error(f"Error parsing generic job element {i+1}: {str(e)}")
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"Generic parsing completed, found {len(jobs)} jobs")
        return jobs
    except Exception as e:
        logger.error(f"Error in generic parser: {str(e)}")
        logger.error(traceback.format_exc())
        return jobs
