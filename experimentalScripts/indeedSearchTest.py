import cloudscraper
import json
import re
from typing import List, Dict, Optional

class Job:
    def __init__(self, data: Dict):
        """
        Initialize Job from the Indeed JSON structure we saw
        """
        self.title = data.get('title', '')
        self.company = data.get('company', '')
        self.location = data.get('formattedLocation', '')
        self.remote_info = data.get('remoteWorkModel', {}).get('text', '')
        self.salary = data.get('salarySnippet', {}).get('text', '')
        self.description = data.get('snippet', '')
        self.post_date = data.get('formattedRelativeTime', '')
        self.link = f"https://www.indeed.com/viewjob?jk={data.get('jobkey', '')}"
        self.company_rating = data.get('companyRating')
        self.review_count = data.get('companyReviewCount')
        self.company_logo = data.get('companyBrandingAttributes', {}).get('logoUrl', '')
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "remote_info": self.remote_info,
            "salary": self.salary,
            "description": self.description,
            "post_date": self.post_date,
            "link": self.link,
            "company_rating": self.company_rating,
            "review_count": self.review_count,
            "company_logo": self.company_logo
        }

def extract_json_from_script(html_content: str) -> Optional[Dict]:
    """
    Extract the mosaic-provider-jobcards JSON data from the HTML
    """
    # Look for the mosaic-provider-jobcards data
    pattern = r'window\.mosaic\.providerData\["mosaic-provider-jobcards"\]\s*=\s*({.*?});?\s*window\.mosaic'
    
    match = re.search(pattern, html_content, re.DOTALL)
    if not match:
        # Try alternative pattern
        pattern = r'"mosaic-provider-jobcards"\s*:\s*({.*?})\s*};'
        match = re.search(pattern, html_content, re.DOTALL)
        
    if match:
        try:
            json_str = match.group(1)
            # Clean up any JS-specific syntax
            json_str = re.sub(r'undefined', 'null', json_str)
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    return None

def search_indeed_rest(query="software engineer", location="Austin, TX", age=1) -> List[Job]:
    """
    REST approach using Indeed's search URL with JSON extraction
    age: number of days (1 = past 24 hours)
    Returns: List of Job objects
    """
    scraper = cloudscraper.create_scraper()
    
    url = "https://www.indeed.com/jobs"
    params = {
        "q": query,
        "l": location,
        "fromage": age,
        "sc": "0kf:attr(DSQF7);",  # Remote jobs filter
        "vjk": "6f27aa2f5b19bad3"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    # Get initial cookies
    scraper.get("https://www.indeed.com", headers=headers)
    
    # Make the search request
    response = scraper.get(url, params=params, headers=headers)
    
    # Extract JSON data from the response
    json_data = extract_json_from_script(response.text)
    
    if json_data and 'metaData' in json_data:
        # Get the results from the correct path
        results = json_data.get('metaData', {}).get('mosaicProviderJobCardsModel', {}).get('results', [])
        return [Job(job_data) for job_data in results]
    
    return []

if __name__ == "__main__":
    # REST approach only since it's working
    try:
        jobs = search_indeed_rest()
        print("\nJobs found via REST:")
        for i, job in enumerate(jobs, 1):
            print(f"\nJob {i}:")
            print(json.dumps(job.to_dict(), indent=2))
        
        print(f"\nTotal jobs found: {len(jobs)}")
        
        # Save raw HTML for debugging
        with open('indeed_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("\nRaw HTML saved to indeed_response.html for debugging")
        
    except Exception as e:
        print(f"REST Error: {e}")
