import cloudscraper
import json
import re
from typing import List, Dict, Optional

class Job:
    def __init__(self, data: Dict):
        """
        Initialize Job from the Indeed JSON structure
        """
        # Essential identifiers
        self.jobkey = data.get('jobkey', '')
        self.job_id = data.get('job_id', '')  # If present
        
        # Basic job info
        self.title = data.get('title', '')
        self.display_title = data.get('displayTitle', '')
        self.normalized_title = data.get('normTitle', '')
        self.company = data.get('company', '')
        self.location = data.get('formattedLocation', '')
        
        # Remote work info
        remote_model = data.get('remoteWorkModel', {})
        self.remote_info = {
            'type': remote_model.get('type', ''),
            'text': remote_model.get('text', ''),
            'inline_text': remote_model.get('inlineText', True)
        }
        
        # Salary info
        salary_data = data.get('salarySnippet', {})
        self.salary = {
            'text': salary_data.get('text', ''),
            'currency': salary_data.get('currency', ''),
            'source': salary_data.get('source', '')
        }
        
        # Company info
        self.company_rating = data.get('companyRating')
        self.company_review_count = data.get('companyReviewCount')
        branding = data.get('companyBrandingAttributes', {})
        self.company_logos = {
            'logo': branding.get('logoUrl', ''),
            'header': branding.get('headerImageUrl', '')
        }
        
        # Dates and timing
        self.post_date = data.get('formattedRelativeTime', '')
        self.pub_date = data.get('pubDate')
        self.create_date = data.get('createDate')
        
        # URLs and links
        self.view_job_link = data.get('viewJobLink', '')
        self.apply_link = data.get('link', '')
        self.company_overview_link = data.get('companyOverviewLink', '')
        
        # Description and metadata
        self.description = data.get('snippet', '')
        self.urgently_hiring = data.get('urgentlyHiring', False)
        self.new_job = data.get('newJob', False)
        self.high_volume_hiring = data.get('highVolumeHiringModel', {}).get('highVolumeHiring', False)
        self.employer_responsive = data.get('employerResponsive', False)
        self.employer_response_time = data.get('employerResponseTime')
        
        # Application data
        self.organic_apply_start_count = data.get('organicApplyStartCount')
        self.indeed_apply_enabled = data.get('indeedApplyEnabled', False)
        
        # Benefits and requirements
        self.taxo_attributes = data.get('taxoAttributes', [])
        requirements_model = data.get('jobCardRequirementsModel', {})
        self.requirements = {
            'job_requirements': requirements_model.get('jobOnlyRequirements', []),
            'job_tags': requirements_model.get('jobTagRequirements', []),
            'screener_questions': requirements_model.get('screenerQuestionRequirements', [])
        }
    
    def to_dict(self) -> Dict:
        return {
            "jobkey": self.jobkey,
            "title": self.title,
            "display_title": self.display_title,
            "normalized_title": self.normalized_title,
            "company": self.company,
            "location": self.location,
            "remote_info": self.remote_info,
            "salary": self.salary,
            "description": self.description,
            "post_date": self.post_date,
            "pub_date": self.pub_date,
            "create_date": self.create_date,
            "view_job_link": self.view_job_link,
            "apply_link": self.apply_link,
            "company_info": {
                "rating": self.company_rating,
                "review_count": self.company_review_count,
                "logos": self.company_logos,
                "overview_link": self.company_overview_link
            },
            "hiring_info": {
                "urgently_hiring": self.urgently_hiring,
                "new_job": self.new_job,
                "high_volume_hiring": self.high_volume_hiring,
                "employer_responsive": self.employer_responsive,
                "employer_response_time": self.employer_response_time,
                "organic_apply_start_count": self.organic_apply_start_count,
                "indeed_apply_enabled": self.indeed_apply_enabled
            },
            "requirements": self.requirements,
            "benefits": self.taxo_attributes
        }
    
    def get_indeed_url(self) -> str:
        """
        Construct the full Indeed URL for this job
        """
        return f"https://www.indeed.com/viewjob?jk={self.jobkey}"

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
    try:
        jobs = search_indeed_rest()
        print("\nJobs found:")
        for i, job in enumerate(jobs, 1):
            print(f"\nJob {i}:")
            print(json.dumps(job.to_dict(), indent=2))
        
        print(f"\nTotal jobs found: {len(jobs)}")
        
    except Exception as e:
        print(f"Error: {e}")
