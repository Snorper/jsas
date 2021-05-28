from bs4 import BeautifulSoup
import sys

from prep.helpers import HttpHelpers

class iJobs:
    def __init__(self, url):
        self.url = url
        self.helpers = HttpHelpers()

    def get(self):
        page = self.helpers.download_page(self.url)

        if page is None:
            sys.exit('Error downloading webpage')

        indeed_jobs = self.__parse_index(page)

        return indeed_jobs

    def __parse_index(self, htmlcontent):
        soup = BeautifulSoup(htmlcontent, 'lxml')
        jobs_container = soup.find(id='resultsCol')
        job_items = jobs_container.find_all('div', class_='jobsearch-SerpJobCard')

        if job_items is None or len(job_items) == 0:
            return []

        all_jobs = []

        for job_elem in job_items:
            url_elem = job_elem.find('a', class_='jobtitle')
            title_elem = job_elem.find('a', class_='jobtitle')
            company_elem = job_elem.find('span', class_='company')
            loc_elem = job_elem.find('span', class_='location')

            if None in (title_elem, company_elem, url_elem, loc_elem):
                continue

            href = url_elem.get('href')
            if href is None:
                continue

            item = {
                "title" : title_elem.text.strip(),
                "company" : company_elem.text.strip(),
                "location" : loc_elem.text.strip(),
                "href" : f'https://www.indeed.com{href}'
            }
            all_jobs.append(item)

        return all_jobs
