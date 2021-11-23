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
        jobs_container = soup.find(id='mosaic-provider-jobcards')
        job_items = jobs_container.find_all('a', class_='resultWithShelf')

        if job_items is None or len(job_items) == 0:
            return []

        all_jobs = []

        for job_elem in job_items:
            url_elem = job_elem
            title_elem = job_elem.find('h2', class_='jobTitle')
            company_elem = job_elem.find('span', class_='companyName')
            loc_elem = job_elem.find('div', class_='companyLocation')

            if None in (title_elem, company_elem, url_elem, loc_elem):
                continue

            href = url_elem.get('href')
            if href is None:
                continue
            title_elem_text = title_elem.text.strip()[3:]

            item = {
                "title" : title_elem_text,
                "company" : company_elem.text.strip(),
                "location" : loc_elem.text.strip(),
                #"href" : href
                "href" : f'https://www.indeed.com{href}'
            }
            all_jobs.append(item)

        return all_jobs
