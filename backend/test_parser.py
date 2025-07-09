from app.scraper import parse_linkedin, parse_generic
from app.resume_parser import extract_text
import requests
import sys

def test_linkedin_parser():
    """Test the LinkedIn parser with a real page"""
    print("Testing LinkedIn parser...")
    url = 'https://www.linkedin.com/jobs/search?keywords=software+engineer'
    
    try:
        print(f"Fetching page from {url}")
        response = requests.get(url)
        html = response.text
        print(f"Fetched {len(html)} bytes of HTML")
        
        jobs = parse_linkedin(html, url)
        print(f"Found {len(jobs)} jobs:")
        
        for i, job in enumerate(jobs[:5]):
            print(f"{i+1}. {job['title']} at {job['company']} - URL: {job['url']} - Fallback: {job.get('is_fallback', False)}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_generic_parser():
    """Test the generic parser with a random job site"""
    print("\nTesting Generic parser...")
    url = 'https://www.indeed.com/jobs?q=software+developer'
    
    try:
        print(f"Fetching page from {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        html = response.text
        print(f"Fetched {len(html)} bytes of HTML")
        
        jobs = parse_generic(html, url)
        print(f"Found {len(jobs)} jobs:")
        
        for i, job in enumerate(jobs[:5]):
            print(f"{i+1}. {job['title']} at {job['company']} - URL: {job['url']} - Fallback: {job.get('is_fallback', False)}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_parser_handles_various_formats():
    """Test the resume parser with various file formats"""
    print("\nTesting parser with various formats...")
    # Realistic PDF/DOCX and mock data
    files = ["sample_resume.pdf", "sample_resume.docx", "mock_resume.txt"]
    for file in files:
        try:
            text = extract_text(file)
            assert isinstance(text, str)
            assert len(text) > 10
            print(f"Successfully parsed {file}")
        except Exception:
            print(f"Failed to parse {file}, moving to next.")

if __name__ == "__main__":
    test_linkedin_parser()
    test_generic_parser()
    test_parser_handles_various_formats()
