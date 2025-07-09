import httpx
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse

logger = logging.getLogger("job_search_app.discovery")

def find_career_page_google(company_name: str, api_key: str, search_engine_id: str) -> str | None:
    """
    Uses Google Custom Search JSON API to find the career page of a company.
    """
    search_url = "https://www.googleapis.com/customsearch/v1"
    query = f'"{company_name}" careers'
    params = {
        'key': "AIzaSyAWmxok9vX-7rmdLe-OisHqALJH_iQQB9k",
        'cx': "f58f6e4a99ecc420c",
        'q': f'"{company_name}" (careers OR jobs OR "work with us")',
        'num': 3  # Fetch top 3 results
    }

    try:
        response = httpx.get(search_url, params=params)
        response.raise_for_status()
        results = response.json()

        if "items" in results:
            for item in results["items"]:
                url = item.get("link")
                if "careers" in url or "jobs" in url:
                    logger.info(f"Found potential career page for {company_name}: {url}")
                    return url
            # If no obvious career page, return the first result
            return results["items"][0].get("link")
            
    except httpx.RequestError as e:
        logger.error(f"Google Search API request failed: {e}")
        return None

def crawl_for_career_page(company_url: str) -> str | None:
    """
    Crawls a company's website to find the career page.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = httpx.get(company_url, headers=headers, follow_redirects=True, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for links with keywords like "careers" or "jobs"
        for link in soup.find_all('a', href=True):
            if any(keyword in link.get_text(strip=True).lower() for keyword in ["careers", "jobs", "work with us"]):
                career_url = urljoin(company_url, link['href'])
                logger.info(f"Found career page by crawling: {career_url}")
                return career_url
                
    except Exception as e:
        logger.error(f"Failed to crawl {company_url}: {e}")
        return None
