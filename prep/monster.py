from bs4 import BeautifulSoup
import sys

from prep.helpers import HttpHelpers

class mJobs:
    def __init__(self, url):
        self.url = url
        self.helpers = HttpHelpers()

    def get(self):
        page = self.helpers.download_page(self.url)

        if page is None:
            sys.exit('Error downloading webpage')

        monster_jobs = self.__parse_index(page)

        return monster_jobs

    def __parse_index(self, htmlcontent):
        soup = BeautifulSoup(htmlcontent, 'lxml')
        jobs_container = soup.find(id='ResultsContainer')
        job_items = jobs_container.find_all('section', class_='card-content')
        if job_items is None or len(job_items) == 0:
            return []

        all_jobs = []

        for job_elem in job_items:
            title_elem = job_elem.find('h2', class_='title')
            company_elem = job_elem.find('div', class_='company')
            url_elem = job_elem.find('a')
            loc_elem = job_elem.find('div', class_='location')
            date_elem= job_elem.find('time')

            if None in (title_elem, company_elem, url_elem, loc_elem, date_elem):
                continue

            href = url_elem.get('href')
            if href is None:
                continue

            item = {
                "title" : title_elem.text.strip(),
                "company" : company_elem.text.strip(),
                "href" : href,
                "loc" : loc_elem.text.strip(),
                "date" : date_elem.text.strip()
            }
            all_jobs.append(item)

        return all_jobs
