import warnings
warnings.filterwarnings("ignore", category=Warning)

import cloudscraper
import json
from bs4 import BeautifulSoup
import re
import html
import time
import random


def clean_description(html_text):
    """
    Clean HTML description into readable text while preserving structure.
    """
    if not html_text:
        return None
        
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # First clean up the structure
    for br in soup.find_all('br'):
        br.replace_with('\n')
    for p in soup.find_all('p'):
        p.append('\n')
    
    # Handle bullet points differently
    for li in soup.find_all('li'):
        # Remove any existing newlines before the bullet point
        if li.string:
            li.string = li.string.strip()
        li.insert_before('• ')
        li.append('\n')
    
    # Get text and clean up extra whitespace
    text = soup.get_text()
    text = html.unescape(text)
    
    # Clean up spacing and structure
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            # Remove extra spaces around bullet points
            if line.startswith('• '):
                line = '• ' + line[2:].lstrip()
            lines.append(line)
    
    # Join lines with proper spacing
    text = '\n'.join(lines)
    
    # Fix multiple newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove any remaining excessive whitespace
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


def setup_scraper():
    """
    Set up cloudscraper with optimal configuration
    """
    return cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True,
            'mobile': False
        },
        debug=False,
        delay=10,  # Allow more time for challenge solving
        interpreter='nodejs'  # Use nodejs interpreter for better challenge solving
    )


def fetch_indeed_job(job_id):
    """
    Fetch job details from Indeed with optimized request handling
    """
    scraper = setup_scraper()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    url = f'https://www.indeed.com/viewjob?jk={job_id}'
    
    try:
        # Add a small initial delay to let cloudscraper warm up
        time.sleep(1)
        
        # Make the request with a longer timeout
        response = scraper.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return parse_indeed_job(response.text)
        else:
            print(f"Request failed with status code: {response.status_code}", file=sys.stderr)
            return None
            
    except Exception as e:
        print(f"Error fetching job: {str(e)}", file=sys.stderr)
        return None


def parse_indeed_job(html_content):
    """
    Parse Indeed job posting HTML with clean description.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Try to get structured data first
    try:
        scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                    return {
                        'title': data.get('title'),
                        'company': data.get('hiringOrganization', {}).get('name'),
                        'location': data.get('jobLocation', {}).get('address', {}).get('addressLocality'),
                        'description': clean_description(data.get('description')),
                        'employment_type': data.get('employmentType'),
                        'date_posted': data.get('datePosted'),
                        'valid_through': data.get('validThrough')
                    }
            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"Error parsing structured data: {str(e)}", file=sys.stderr)

    # Fallback to HTML parsing if needed
    return {
        'title': soup.select_one('h1.jobsearch-JobInfoHeader-title').get_text(strip=True) if soup.select_one('h1.jobsearch-JobInfoHeader-title') else None,
        'company': soup.select_one('[data-company-name="true"]').get_text(strip=True) if soup.select_one('[data-company-name="true"]') else None,
        'location': soup.select_one('[data-testid="inlineHeader-companyLocation"]').get_text(strip=True) if soup.select_one('[data-testid="inlineHeader-companyLocation"]') else None,
        'description': clean_description(str(soup.select_one('#jobDescriptionText'))) if soup.select_one('#jobDescriptionText') else None
    }


if __name__ == "__main__":
    import sys
    
    job_id = "d7442c53b66f9e83"
    result = fetch_indeed_job(job_id)
    
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Failed to fetch job details", file=sys.stderr)
